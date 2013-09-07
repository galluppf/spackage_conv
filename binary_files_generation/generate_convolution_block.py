#!/usr/bin/python
"""
This module is used to generate kernels in SDRAM starting for convolutional modules 
(cell_type Convolution). 

It cycles all the Convolution type part_populations and evaluates the parameter 'kernel' 
for each projection associated to the convolutional core x,y,p 

.. moduleauthor:: Francesco Galluppi, SpiNNaker Project, University of Manchester. francesco.galluppi@cs.man.ac.uk
"""

import sys
import pacman
import os
import struct

CONVOLUTIONAL_IMAGE_NAME = 'app_convolution.aplx'   # TODO do more properly with module name
DEBUG = pacman.pacman_configuration.getboolean('convolution', 'debug')
SDRAM_BASE = 0x70000000

##### INSERTED FOR LOOKUP TABLE GENERATION
LOOKUP_WORDS_PER_ENTRY = 5  # each lookup entry has 5 words

OFFSET_CORE_ID = 11
MASK_CORE_ID = 0xF # (4 bits)

OFFSET_X_CHIP_ID = 24
MASK_X_CHIP_ID = 0xFF # 8bits

OFFSET_Y_CHIP_ID = 16
MASK_Y_CHIP_ID = 0xFF # 8bits

    
def patch_SDRAM_for_convolution(db):
    core_list = [ {'x' : c['x'], 'y' : c['y'],'p' : c['p']} 
        for c in db.get_image_map() if c['image_name'] == CONVOLUTIONAL_IMAGE_NAME ]
    
    for c in core_list:
        compute_sdram_block(c, db)
    

def compute_sdram_block(c, db):
    """
    Gets the kernels and writes the lookup file and returns the string containing the list of kernels
    """
    memory_pointer_base = 0     #   the pointer for this file increments from this base and the length of out_string (cumulative)
    out_string = ""
    r_key_map = db.get_routing_key_map()
    
    print '[ kernel writer ] : evaluating core', c['x'], c['y'], c['p']
    
    filename = '%s/SDRAM_%d_%d.dat' % (pacman.BINARIES_DIRECTORY, c['x'], c['y'])
    sdram_file = open(filename, 'ab')
    memory_pointer = SDRAM_BASE + (os.path.getsize(filename))       # size is in bytes
    print memory_pointer

    lookup_file_name = '%s/lktbl_%d_%d_%d.dat' % (pacman.BINARIES_DIRECTORY, c['x'], c['y'], c['p'])
    lookup_data = []

    
    # extracting all projections that have this postsynaptic core
    projections = db.generic_select('pop.size as post_part_pop_size, proj.id as proj_id, proj.*, processors.*, pop.start_id, pop.end_id, pop.offset', 'part_projections proj, part_populations as pop, map, processors where postsynaptic_part_population_id = pop.id and map.processor_group_id = pop.processor_group_id and processors.id = map.processor_id and processors.x=%d and processors.y = %d and p = %d' % (c['x'], c['y'], c['p']))
    
    # Getting all the pre part_population that project to this core
    pre_part_populations = db.get_part_populations()
        
    if DEBUG:   
        for pre_part_population in pre_part_populations:    
            print 'pre_part_population: ', pre_part_population['id'], pre_part_population['size'], pre_part_population['population_core_offset']
            print "computing SDRAM entry for core %s at offset %x, length %d" % (c, memory_pointer, len(projections))

    # Extract a list with distinct pre part_population ids
    distinct_pre_pop = [ el['presynaptic_part_population_id'] for el in projections ]        
    distinct_pre_pop = list(set(distinct_pre_pop))  #   list(set(list)) eliminates dupicates in the list 
    
    # getting the dynamic translation from the DB
    synaptic_translations = db.get_synaptic_translation(c['x'], c['y'], c['p'])
        
    #if DEBUG:	print 'synaptic_translations', synaptic_translations

    #   cycling distinct pre part_populations
    #       cycling distinct projections from population (build cumulative synaptic matrix portion, not translated)
    #           cycling different synapse types and translating


    # Every distinct part_population will have a different entry, cumulative of all its contributed projections
    for p in distinct_pre_pop:  # for every source population we need to build a synaptic block. This is the main loop of the file
        # Retrie
        distinct_projections_from_pop = [ el for el in projections if el['presynaptic_part_population_id'] == p ]
        pre_proc_coord = db.generic_select('processors.x, processors.y, processors.p', 'part_populations as pop, map, processors where pop.id = %d and map.processor_group_id = pop.processor_group_id and processors.id = map.processor_id' % p)[0]
        
        # Every pre part_population as a distinct block, hence a different pointer, which is calculated based on the base pointer passed and the length of what has been done so far
        
        # looping
        for d in distinct_projections_from_pop:     # d['proj_id'] is the part_projection_id
            print d
            parameters = eval(d['parameters'])

            memory_pointer = memory_pointer + len(out_string)

            presynaptic_population = [ p for p in pre_part_populations if p['id']== d['presynaptic_part_population_id'] ][0]
            
            # gets the starting r_key of the part_population
            r_key = (r for r in r_key_map if r['part_population_id'] == presynaptic_population['id']).next()            
            
            # calculates the routing key
            r_key = (r_key['x'] << OFFSET_X_CHIP_ID) | (r_key['y'] << OFFSET_Y_CHIP_ID)  | (r_key['p'] << OFFSET_CORE_ID)
            
            # appends the info needed to generate the lookup table entry
            lookup_data.append({'memory_pointer':memory_pointer, 
                                'synaptic_row_length':len(parameters['weights']), 
                                'mask': eval(presynaptic_population['mask']),
                                'r_key': r_key})

            weights = [ p*1 for p in parameters['weights'] ]
            out_string += struct.pack('%di' % len(parameters['weights']), *weights)

    
    sdram_file.write(out_string)
    sdram_file.close()  
    
        # write lookup_data
    CONCLUSIVE_WORDS_SIZE = 5
    LOOKUP_HEADER_SIZE = 1
    lookup_file = open(lookup_file_name,'w+')
    # calculates the size in bytes of the LUT
    lookup_file.write(struct.pack("<I", len(lookup_data) * LOOKUP_WORDS_PER_ENTRY * 4 + (CONCLUSIVE_WORDS_SIZE * 4)))

    # sorts the lookup table # do I need to sort it???
    lookup_data_sorted = sorted(lookup_data, key=lambda k: k['r_key'])
    
    print lookup_data_sorted
    
    for l in lookup_data_sorted:
        lookup_file.write(struct.pack("<IIIII", 
                                        l['r_key'],         #   fasc addr
                                        l['mask'],          #   mask
                                        l['memory_pointer'], 
                                        0,                  #   linear search
                                        l['synaptic_row_length']
                                        ))

    # writes footer and closes the file
    lookup_file.write(struct.pack("<IIIII", 0xFFFFFFFF, 0, 0, 0, 0))
    lookup_file.close()


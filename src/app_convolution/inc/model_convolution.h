#ifndef __MODEL_CONVOLUTION_H__
#define __MODEL_CONVOLUTION_H__


#define LOG_P1                  (8)
#define LOG_P2                  (16)
#define P1                      (1 << LOG_P1) // 256
#define P2                      (1 << LOG_P2) // 65536
#define IZK_CONST_1             (4*P2/100)
#define IZK_CONST_2             (5*P1)
#define IZK_CONST_3             (140*P1)
#define IZK_THRESHOLD           (30)

uint LOOKUP_MASK = 0xFFFFF800;

typedef struct
{
    int v;     // int(value)*65536
    uint time_last_input_spike;
    uint time_last_output_spike;    
} neuron_t;


#endif


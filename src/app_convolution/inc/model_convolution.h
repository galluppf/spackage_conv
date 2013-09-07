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



typedef struct
{
    short v;     // int(value)*256
    short v_thresh;     // int(value)*256
    short v_reset;     // int(value)*256
    short v_rest;     // int(value)*256
    short tau_refrac;     // int(value)
    short tau_refrac_clock;     // int(value)
    int tau_m;     // int(65536/value)

} neuron_t;


#endif


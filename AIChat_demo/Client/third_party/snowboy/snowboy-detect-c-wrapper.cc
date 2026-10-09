// 桩实现：用音量检测代替 snowboy 唤醒词
#include "include/snowboy-detect-c-wrapper.h"
#include <cstring>
#include <cmath>
#include <cstdio>

struct SnowboyDetect {
    int dummy;
};

extern "C" {

SnowboyDetect* SnowboyDetectConstructor(const char* resource_filename, const char* model_str) {
    (void)resource_filename;
    (void)model_str;
    printf("[STUB] SnowboyDetectConstructor called\n");
    return new SnowboyDetect();
}

bool SnowboyDetectReset(SnowboyDetect* detector) { (void)detector; return true; }

int SnowboyDetectRunDetection(SnowboyDetect* detector, const int16_t* data, int array_length, bool is_end) {
    (void)detector; (void)is_end;
    if (!data || array_length <= 0) return 0;
    double sum = 0.0;
    for (int i = 0; i < array_length; i++) {
        double v = (double)data[i];
        sum += v * v;
    }
    double rms = sqrt(sum / array_length);
    if (rms > 500.0) {
        printf("[STUB] Wake by volume, RMS=%.1f\n", rms);
        return 1;
    }
    return 0;
}

void SnowboyDetectSetSensitivity(SnowboyDetect* d, const char* s) { (void)d; (void)s; }
void SnowboyDetectSetAudioGain(SnowboyDetect* d, float g) { (void)d; (void)g; }
void SnowboyDetectApplyFrontend(SnowboyDetect* d, bool apply) { (void)d; (void)apply; }
void SnowboyDetectDestructor(SnowboyDetect* d) { delete d; }

} // extern "C"

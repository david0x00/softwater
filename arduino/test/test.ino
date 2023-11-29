#include "src/microcode/hal/hal.h"
#include "src/microcode/util/log.h"
#include "src/microcode/MCP23S08/mcp23s08.h"
#include "src/microcode/ADS1120/ads1120.h"
#include "src/microcode/util/rate.h"

#include <Adafruit_NeoPixel.h>
#include <Adafruit_BNO08x.h>
#include <SPI.h>

#define MCP_CS  22
#define MCP_RST 27

#define ADC_CS  15
#define ADC_RST 39

#define IMU_CS  5
#define IMU_INT 25
#define IMU_RST 14

#define PXL_PIN 21
#define NUM_PXL 4

SPIClass spi(VSPI);
MCP23S08 mcp(&spi, MCP_CS, MCP_RST);
ADS1120 adc(&spi, ADC_CS, ADC_RST);
Adafruit_BNO08x imu(IMU_RST);
Adafruit_NeoPixel pixel(NUM_PXL, PXL_PIN, NEO_GRB + NEO_KHZ800);

Rate r(1);
Rate g(2);
Rate b(3);

Rate pixelSend(100);
Rate debug(5);

struct euler_t 
{
  float yaw;
  float pitch;
  float roll;
} ypr;
sh2_SensorValue_t sensorValue;

void setup()
{
    sysBeginDebug(115200);

    unsigned failures = 0;
    log("init", "Begin initialization...");
    
    spi.begin();

    log("init", "MCP GPIO Extender", false);
    if (!mcp.begin())
    {
        logf();
        failures++;
    }
    else
        logs();

    log("init", "BNO085 IMU", false);
    if (!imu.begin_SPI(5, 25, &spi))
    {
        logf();
        failures++;
    }
    else
        logs();

    log("init", "ADS1120 ADC", false);
    if (!adc.begin())
    {
        logf();
        failures++;
    }
    else
        logs();

    log("init", "Initialization complete with (", false);
    logc(failures, false);
    logc(") failures");

    for (unsigned i = 0; i < 8; i++)
        mcp.setMode(i, OUTPUT);
    
    adc.setGain(ADS1120::Gain1);
    adc.setDataRate(ADS1120::T2000);
    adc.setConversionMode(ADS1120::Continuous);
    adc.setVoltageRef(ADS1120::External_REFP0_REFN0); 
    adc.setMux(ADS1120::AIN0_AVSS);
}

void quaternionToEuler(float qr, float qi, float qj, float qk, euler_t* ypr, bool degrees=false)
{
    float sqr = sq(qr);
    float sqi = sq(qi);
    float sqj = sq(qj);
    float sqk = sq(qk);

    ypr->yaw = atan2(2.0 * (qi * qj + qk * qr), (sqi - sqj - sqk + sqr));
    ypr->pitch = asin(-2.0 * (qi * qk - qj * qr) / (sqi + sqj + sqk + sqr));
    ypr->roll = atan2(2.0 * (qj * qk + qi * qr), (-sqi - sqj + sqk + sqr));

    if (degrees) 
    {
        ypr->yaw *= RAD_TO_DEG;
        ypr->pitch *= RAD_TO_DEG;
        ypr->roll *= RAD_TO_DEG;
    }
}

void loop()
{
    if (imu.wasReset())
        imu.enableReport(SH2_ARVR_STABILIZED_RV, 5000);
    
    if (imu.getSensorEvent(&sensorValue))
    {
        switch (sensorValue.sensorId) 
        {
            case SH2_ARVR_STABILIZED_RV:
            {
                quaternionToEuler(
                    sensorValue.un.arvrStabilizedRV.real, 
                    sensorValue.un.arvrStabilizedRV.i,
                    sensorValue.un.arvrStabilizedRV.j,
                    sensorValue.un.arvrStabilizedRV.k,
                    &ypr, 
                    true);
            }
        }
    }

    if (pixelSend.isReady())
    {
        for (unsigned i = 0; i < 4; i++)
        {
            pixel.setPixelColor(i, 
                pixel.Color(
                    r.getStageCos(0.1f * i) * 10, 
                    g.getStageCos(0.1f * i) * 10, 
                    b.getStageCos(0.1f * i) * 10));
        }
        pixel.show();
    }
    
    if (debug.isReady())
    {
        logc("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n");
        log("ADC", "Voltage: ", false);
        logc(adc.readVoltage());
        log("IMU", "Yaw: ", false);
        logc(ypr.yaw, false);
        logc("\tPitch: ", false);
        logc(ypr.pitch, false);
        logc("\tRoll: ", false);
        logc(ypr.roll);
    }
}

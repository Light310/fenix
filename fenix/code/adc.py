import mcp3008
import time

def convert_to_voltage(adc_value):
    return round(3.3*adc_value/1024, 2)


def single_battery_voltage(adc_value):
    return round(1.5*convert_to_voltage(adc_value),2)


adc = mcp3008.MCP3008()
for i in range(100):
    adc_value = int(adc.read([mcp3008.CH2])[0])
    print ('{0}\t{1}\t{2}'.format(adc.read([mcp3008.CH0]),adc_value, single_battery_voltage(adc_value)))
    time.sleep(0.2)
adc.close()
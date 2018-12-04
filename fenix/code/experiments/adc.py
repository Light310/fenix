import mcp3008
import time

adc = mcp3008.MCP3008()
for i in range(100):
    print adc.read([mcp3008.CH0]) # prints raw data [CH0]
    time.sleep(0.2)
adc.close()
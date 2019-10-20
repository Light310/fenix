import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


class ADC:
    def __init__(self):
        # Hardware SPI configuration:
        SPI_PORT = 0
        SPI_DEVICE = 0
        self.mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

    @staticmethod
    def _convert_to_voltage(adc_value):
        return round(3.3 * adc_value / 1024, 2)

    def read_voltage_rpi(self):
        return round(1.5 * self._convert_to_voltage(self.read_values(channel=0)), 2)

    def read_voltage_servos_normalized(self):
        # normalizing to a single battery (3.3 - 4.2V), tho there are 2 batteries
        return round(1.5 * self._convert_to_voltage(self.read_values(channel=1)), 2)

    def read_values(self, channel=None):
        if channel is None:
            values = [0] * 8
            for i in range(8):
                # The read_adc function will get the value of the specified channel (0-7).
                values[i] = self.mcp.read_adc(i)
            return values
        else:
            return self.mcp.read_adc(channel)

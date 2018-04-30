from . import *
from udsoncan.Response import Response
from udsoncan.exceptions import *

class WriteMemoryByAddress(BaseService):
	_sid = 0x3D
	_use_subfunction = False

	supported_negative_response = [	 Response.Code.IncorrectMessageLegthOrInvalidFormat,
							Response.Code.ConditionsNotCorrect,
							Response.Code.RequestOutOfRange,
							Response.Code.SecurityAccessDenied,
							Response.Code.GeneralProgrammingFailure
							]

	@classmethod
	def make_request(cls, memory_location, data):
		from udsoncan import Request, MemoryLocation

		if not isinstance(memory_location, MemoryLocation):
			raise ValueError('Given memory location must be an instance of MemoryLocation')

		if not isinstance(data, bytes):
			raise ValueError('data must be a bytes object')
		request =  Request(service=cls)
		
		request.data = b''
		request.data += memory_location.alfid.get_byte() # AddressAndLengthFormatIdentifier
		request.data += memory_location.get_address_bytes()
		request.data += memory_location.get_memorysize_bytes()
		request.data += data

		return request

	@classmethod
	def interpret_response(cls, response, memory_location):
		from udsoncan import MemoryLocation

		if not isinstance(memory_location, MemoryLocation):
			raise ValueError('Given memory location must be an instance of MemoryLocation')

		address_bytes 		= memory_location.get_address_bytes()
		memorysize_bytes 	=  memory_location.get_memorysize_bytes()

		expected_response_size = 1 + len(address_bytes) + len(memorysize_bytes)
		if len(response.data) < expected_response_size:
			raise InvalidResponseException(response, 'Repsonse should be at least %d bytes' % (expected_response_size))

		response.service_data = cls.ResponseData()
		response.service_data.alfid_echo = response.data[0]
		
		offset=1
		length = len( memory_location.get_address_bytes())
		address_echo = response.data[1:1+length]
		offset+=length
		length = len(memory_location.get_memorysize_bytes())
		memorysize_echo = response.data[offset:offset+length]

		response.service_data.memory_location_echo = MemoryLocation.from_bytes(address_bytes=address_echo, memorysize_bytes=memorysize_echo)

	class ResponseData(BaseResponseData):
		def __init__(self):
			super().__init__(WriteMemoryByAddress)
			self.alfid_echo = None
			self.memory_location_echo = None
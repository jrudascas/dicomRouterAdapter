#Token asociado al usuario con privilegios de consumo de la API del CORE de IA
API_KEY = '21d537327ac4afa95f77059294421fca83575958'

#EndPoint base de la API del CORE de IA
API_URL = 'http://127.0.0.1:8000/'

END_POINT_RUN_PREDICTION = 'request/'
END_POINT_FIND_MODEL_BY_ID = 'model/?name='

#Lista de modelos a ejecutar en cada llamado. La estructura de este parametro es una lista de tuplas. Donde cada tupla
#contendrá en el nombre del modelo a ejecutar y un valor de verdad que indica si la respuesta visual de la ejecución
#del modelo, se debe retornar como una captura secundaria.
MODELS_TO_SEND = [('ChestXNetv1.0', True), ('COVID19v1.0', True)]

#Dirección del host donde se inicia el DICOM Router
SERVER_HOST_ADDRESS = '127.0.0.1'

#Puerto del host donde se inicia el DICOM Router Adapter
SERVER_HOST_PORT = 11112

#Application Entity Title del servicio del DICOM Router Adapter
SERVER_HOST_AET = 'DAEMON'

#---------------------------------------------------------------------------------------------------------------------
#Si el valor que acompaña en tupla el nombre de cada modelo es igual a True, entonces la respuesta visual se retornará
#como un Secondary Capture al PACS detallado a continuación:
SERVER_REMOTE_ADDRESS = '198.211.117.182'
SERVER_REMOTE_PORT = 11112
SERVER_REMOTE_AET = 'DCM4CHEE'
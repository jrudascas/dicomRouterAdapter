# Token asociado al usuario con privilegios de consumo de la API del CORE de IA
API_KEY = '21d537327ac4afa95f77059294421fca83575958'

# EndPoint base de la API del CORE de IA
API_URL = 'http://127.0.0.1:8000/'

END_POINT_RUN_PREDICTION = 'request/'
END_POINT_FIND_MODEL_BY_ID = 'model/?name='

# Lista de modelos a ejecutar en cada llamado. La estructura de este parametro es una lista de tuplas. Donde cada tupla
# contendrá en el nombre del modelo a ejecutar y un valor de verdad que indica si la respuesta visual de la ejecución
# del modelo, se debe retornar como una captura secundaria.
# MODELS_TO_SEND = [('COVID19v1.0', True)]
# MODELS_TO_SEND = [('ChestXNetv1.0', True), ('COVID19v1.0', True)]

CHESTXNET_FILTER = {
    ('0x0018', '0x0015'): ['CHEST', 'TORAX', 'BREAST'],
    ('0x0008', '0x0060'): ['CR'],
    ('0x0008', '0x103E'): ''
}

COVID_FILTER = {
    ('0x0018', '0x0015'): ['CHEST', 'TORAX', 'BREAST'],
    ('0x0008', '0x0060'): ['CR'],
    ('0x0008', '0x103E'): ''
}

COVID_CT_FILTER = {
    ('0x0018', '0x0015'): ['CHEST', 'TORAX', 'BREAST', 'ABDOMEN'],
    ('0x0008', '0x0060'): ['CT'],
    ('0x0020', '0x0013'): [50],
    ('0x0008', '0x103E'): ['Lung 3.0', 'Lung 3.000', 'AXIAL MEDIASTINO', 'AXIAL PULMON']
}

COVID_CT_TAGS = [
    #('', ('0x0008', '0x1030')), #Study Description
    #('', ('0x0008', '0x103E')), #Serie Description
    ('Slide Number: ', ('0x0020', '0x0013')), #Instance Number
]

MODELS_TO_SEND = [#('ChestXNetv1.0', False, (1024, 1024), CHESTXNET_FILTER, None),
                  #('COVID19v1.0', False, (1024, 1024), COVID_FILTER, None),
                  ('COVID19CTv1.0', True, (512, 512), COVID_CT_FILTER, COVID_CT_TAGS)
                  ]

# Dirección del host donde se inicia el DICOM Router
SERVER_HOST_ADDRESS = '127.0.0.1'

# Puerto del host donde se inicia el DICOM Router Adapter
SERVER_HOST_PORT = 11112

# Application Entity Title del servicio del DICOM Router Adapter
SERVER_HOST_AET = 'DAEMON'

# ---------------------------------------------------------------------------------------------------------------------
# Si el valor que acompaña en tupla el nombre de cada modelo es igual a True, entonces la respuesta visual se retornará
# como un Secondary Capture al PACS detallado a continuación:
SERVER_REMOTE_ADDRESS = '192.34.58.162'
SERVER_REMOTE_PORT = 11112
SERVER_REMOTE_AET = 'ESSENTIALDEMO'

from security import Credentials
from firebase_admin import initialize_app, firestore
from firebase_admin.credentials import Certificate
from db import FirestoreDB
from db.models import OHLCV, OHLCVBatch
import json
from google.cloud.firestore import CollectionReference, DocumentReference
from pytorch_tsmixer import predict_price
from adapters import TSAdapter
from uuid import uuid4
app = initialize_app(Certificate(Credentials("firebase").load()))
db = FirestoreDB(app)
tsadapter=TSAdapter()
dbr=firestore.client(app)
batch=dbr.collection("Batch_OHLCV")
doc=batch.document("BTC-USDT")
sub_coll=doc.collection("BTC-USDT_batches")
query=sub_coll.limit_to_last(1)
data_objs=[]

for snap in query.get():
    data=json.loads(snap.get("batch"))
    data_objs.extend(data)

pasrse_objs=tsadapter.parse_batch(ohlcv_batches=data_objs)
# predict_price(float(data_objs[0]))
predicted_output=predict_price(pasrse_objs)
tensor_cpu = predicted_output.cpu()
tensor_list = tensor_cpu.tolist()
formatted_data = []
for sublist in tensor_list:
    for item in sublist:
        formatted_item = [str(i) for i in item]
        formatted_data.append(formatted_item)

# Convert the list to a string
formatted_str = str(formatted_data)
ts_batch=dbr.collection("Batch_TIMESERIES")
ts_doc=ts_batch.document("BTC-USDT")
ts_sub_coll=ts_doc.collection("BTC-USDT_batches")
ts_sub_doc = ts_sub_coll.document(str(uuid4()))
doc = ts_sub_doc.get()

# If the document exists, generate a new UUID
while doc.exists:
    new_uuid = str(uuid4())
    ts_sub_doc = ts_sub_coll.document(new_uuid)
    doc = ts_sub_doc.get()
ts_sub_doc.set({"predicted_batches":formatted_str})

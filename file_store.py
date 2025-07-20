import json
import hashlib
import os
import base64
from tendermint.abci.types_pb2 import (
    ResponseInfo,
    ResponseInitChain,
    ResponseCheckTx,
    ResponseDeliverTx,
    ResponseQuery,
    ResponseCommit,
)
from abci.server import ABCIServer
from abci.application import BaseApplication, OkCode, ErrorCode


class FileStoreApp(BaseApplication):
    def __init__(self):
        self.state = {}
        self.last_block_height = 0
        self.STORAGE_DIR = "./storage"
        os.makedirs(self.STORAGE_DIR, exist_ok=True)

    def info(self, req) -> ResponseInfo:
        return ResponseInfo(
            version=req.version,
            last_block_height=self.last_block_height,
            last_block_app_hash=b""
        )

    def init_chain(self, req) -> ResponseInitChain:
        self.state = {}
        self.last_block_height = 0
        return ResponseInitChain()

    def check_tx(self, req) -> ResponseCheckTx:
        try:
            tx = req.decode("utf-8")
            if ":" not in tx:
                return ResponseCheckTx(code=1, log="Invalid tx format")
            return ResponseCheckTx(code=0)
        except Exception as e:
            return ResponseCheckTx(code=1, log=str(e))

    def deliver_tx(self, req) -> ResponseDeliverTx:
        try:
            tx = req.decode("utf-8")
            print(f"Received tx: {tx}")  # Debug line

            if ':' not in tx:
                print("Invalid tx format")
                return ResponseDeliverTx(code=1)

            filename, b64_content = tx.split(":", 1)
            content = base64.b64decode(b64_content.encode('utf-8'))

            filepath = os.path.join(self.STORAGE_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(content)

            self.last_block_height += 1
            print(f"Saved file: {filename} (base64 decoded)")

            return ResponseDeliverTx(code=0)
        except Exception as e:
            print(f"Error in deliver_tx: {e}")  # Debug
            return ResponseDeliverTx(code=1, log=str(e))

    def query(self, req) -> ResponseQuery:
        try:
            filename = req.data.decode("utf-8")
            filepath = os.path.join(self.STORAGE_DIR, filename)

            if not os.path.isfile(filepath):
                return ResponseQuery(code=ErrorCode, log="File not found")

            with open(filepath, "rb") as f:
                content = f.read()

            b64_content = base64.b64encode(content).decode("utf-8")
            return ResponseQuery(code=OkCode, value=b64_content.encode("utf-8"))
        except Exception as e:
            return ResponseQuery(code=ErrorCode, log=f"Query error: {str(e)}")

    def commit(self) -> ResponseCommit:
        h = hashlib.sha256()

        if not os.path.exists(self.STORAGE_DIR):
            os.makedirs(self.STORAGE_DIR)
            return ResponseCommit(data=h.digest()[:8])  # empty hash

        for filename in sorted(os.listdir(self.STORAGE_DIR)):
            path = os.path.join(self.STORAGE_DIR, filename)
            if os.path.isfile(path):
                h.update(filename.encode())
                with open(path, "rb") as f:
                    h.update(f.read())
        return ResponseCommit(data=h.digest()[:8])


def main():
    app = ABCIServer(app=FileStoreApp())
    app.run()


if __name__ == "__main__":
    main()

from matrix_client.api import MatrixHttpApi
from matrix_client.client import MatrixClient
from matrix_client.room import Room
import base64

class CrawlerMatrixClient:
    def __init__(self, token, server, roomid):
        self.server = server
        self.roomid = roomid
        self.token = token
        self.APIWrapper = MatrixHttpApi("https://{}".format(self.server), token=self.token)
        self.next_batch = self.APIWrapper.sync().get("next_batch")
        print("client initialized")

    def getChunk(self):
        b = self.APIWrapper.get_room_messages(self.roomid, self.next_batch, "b", limit=100)
        c = b.get("chunk")
        self.next_batch = b.get("end")
        return c

    def try_recover_suspend(self, output_file, contents, timestamps, names, message_count):
        with open(output_file, "r") as handle:
            a = handle.readlines()
            if a[len(a)-1] == "sus":
                print("\n\nrestoring from suspend'\n\n")
                self.next_batch = a[len(a)-2]
                a = a[:-2]
                for element in a:
                    b = element.split(";")
                    timestamps.append(b[0])
                    names.append(b[1])
                    contents.append(b[2])
                print("restored")
                return message_count - len(a) + 1 

    def suspend(self, contents, timestamps, names, output_file):
        print("suspending to output_file")
        with open(output_file, "w+") as handle:
            for i in range(len(contents)-1):
                handle.write(str(timestamps[i]))
                handle.write(";")
                handle.write(str(names[i]))
                handle.write(";")
                content = base64.b64encode(str.encode(str(contents[i]))).decode()
                handle.write(content)
                handle.write("\n")
            handle.write(self.next_batch)
            handle.write("\n")
            handle.write("sus")

    def dump_message_events(self, message_count, output_file):
        contents = []
        timestamps = []
        names = []
        try:
            message_count = self.try_recover_suspend(output_file, contents, timestamps, names, message_count)
        except:
            pass
        try:
            count = message_count // 100
            for progress in range(count):
                chunk = self.getChunk()
                for element in chunk:
                    content = element.get("content").get("body")
                    if content is not None:
                        timestamps.append(element.get("origin_server_ts"))
                        contents.append(content)
                        names.append(element.get("sender"))
                print("haha progress bar go brr {} out of {}".format(progress, count), end='\r')
            with open(output_file, "w+") as handle:
                for i in range(len(contents)-1):
                    handle.write(str(timestamps[i]))
                    handle.write(";")
                    handle.write(str(names[i]))
                    handle.write(";")
                    content = base64.b64encode(str.encode(str(contents[i]))).decode()
                    handle.write(content)
                    handle.write("\n")
                handle.write(self.next_batch)
                handle.write("\n")
                handle.write("sus")
        except KeyboardInterrupt:
            self.suspend(contents, timestamps, names, output_file)

if __name__ == "__main__":
    Client = CrawlerMatrixClient(open("secret.txt", "r").read(), "matrix.org", "!VYsYJQNEpQSJlMMxiC:fam-ribbers.com")
    Client.dump_message_events(200000, "new_dump_offtopic")
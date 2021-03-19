from matrix_client.api import MatrixHttpApi
from matrix_client.client import MatrixClient
from matrix_client.room import Room

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
    def dump_message_events(self, message_count, output_file):
        events = []
        try:
            message_count = self.try_recover_suspend(output_file, events, message_count)
        except:
            pass
        try:
            count = message_count // 100
            for progress in range(count):
                chunk = self.getChunk()
                for element in chunk:
                    events.append(element.get("origin_server_ts"))
                print("haha progress bar go brr {} out of {}".format(progress, count), end='\r')
            with open(output_file, "w+") as handle:
                for element in events:
                    handle.write(str(element))
                    handle.write("\n")
        except KeyboardInterrupt:
            self.suspend(events, output_file)
    def try_recover_suspend(self, output_file, events, message_count):
        with open(output_file, "r") as handle:
            a = handle.readlines()
            if a[len(a)-1] == "sus":
                print("restoring from suspend")
                self.next_batch = a[len(a)-2]
                a = a[:-2]
                for element in a:
                    events.append(element.strip())
                return message_count - len(a) + 1 

    def suspend(self, processed_events, output_file):
        print("suspending to output_file")
        with open(output_file, "w+") as handle:
            for element in processed_events:
                handle.write(str(element))
                handle.write("\n")
            handle.write(self.next_batch)
            handle.write("\n")
            handle.write("sus")
if __name__ == "__main__":
    Client = CrawlerMatrixClient(open("secret.txt", "r").read(), "matrix.org", "!KIwsdPeEnTTmPnMpMv:fam-ribbers.com")
    Client.dump_message_events(400000, "the_grand_dump_mainl1ne")
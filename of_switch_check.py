from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls

#imports for REST API
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from webob import Response
import json

class OFSwitchCheck(app_manager.RyuApp):

    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(OFSwitchCheck, self).__init__(*args, **kwargs)
        self.datapaths = {}
        wsgi = kwargs['wsgi']
        wsgi.register(OFCheckAPI, {"of_app" : self})

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser

        self.datapaths[datapath.id] = {}
        self.datapaths[datapath.id]["num_tables"] = ev.msg.n_tables

        req = parser.OFPPortDescStatsRequest(datapath, 0)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_handler(self, ev):
        datapath = ev.msg.datapath

        ports = {}

        for port in ev.msg.body:
            ports[port.port_no] = port.name.decode("utf-8")

        self.datapaths[datapath.id]["ports"] = ports
        print(self.datapaths)


class OFCheckAPI(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(OFCheckAPI, self).__init__(req, link, data, **config)
        self.of_app = data["of_app"]

    @route("ofcheck", "/get_all", methods=["GET"])
    def get_all_info(self, req, **kwargs):
        body = json.dumps(self.of_app.datapaths).encode('utf-8')
        return Response(content_type='application/json', body=body)

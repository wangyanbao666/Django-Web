from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializer import RoomSerializer

@api_view(["GET"])
def get_routes(req):
    routes = [
        "GET api/",
        "GET api/rooms",
        "GET api/rooms/:id",
    ]
    return Response(routes)


@api_view(["GET"])
def get_rooms(req, pk):
    id = pk
    try:
        room = Room.objects.get(id=id)
        room_serializer = RoomSerializer(room, many=False)
        return Response(room_serializer.data)
    except:
        return Response("None data found")

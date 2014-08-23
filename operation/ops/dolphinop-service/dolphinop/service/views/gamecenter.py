from django.conf import settings
from django.views.decorators.http import require_GET
from django.utils.encoding import smart_str
from dolphinop.service.errors import parameter_error, resource_not_modified
from dolphinop.service.views import json_response, MongodbStorage, IncrementalId, cursor_to_list
from dolphinop.service.utils import get_parameter_GET


class GameCenterMongodbStorage(MongodbStorage):

    db_name = "dolphinop"

    def __init__(self, conn_str):
        super(GameCenterMongodbStorage, self).__init__(conn_str, self.db_name)
        self._ids = IncrementalId(self._db)

    def queryApplication(self, app_id):
        returns = self._db.gc_application.find(
            {'id': int(app_id)}, {'_id': 0}) if app_id != None else []
        return returns[0] if returns.count() else {}

    @cursor_to_list
    def queryCategory(self):
        return self._db.gc_category.find()

    @cursor_to_list
    def queryBanner(self):
        returns = self._db.gc_banner.find({}, {'pk': 0})
        return returns

    @cursor_to_list
    def querySubject(self):
        return self._db.gc_subject.find()

    @cursor_to_list
    def querySearch(self, q):
        return self._db.gc_application.find({'name': {'$regex': smart_str(q), '$options': 'im'}}) if q else []

    def queryAppList(self, m, start, count, cat_id, cat_type):
        filters = {
            'id': 1,
            'name': 1,
            'developer': 1,
            'icon_url': 1,
            'rating': 1,
            'category_name': 1,
            'category_id': 1,
        }
        cat_id = int(cat_id)
        start = int(start)
        count = int(count)
        print 'm: %s and cat : %d' % (m, cat_id)
        lists = []
        try:
            if m == 'cat':
                returns = self._db.gc_applists.find(
                    {'name': cat_type}, {'lists': 1})
                lists += [j for i in returns for j in i['lists']
                          if (j['category_id'] == cat_id and j['id'] > start)]

            if m == 'lists':
                if cat_type:
                    returns = self._db.gc_applists.find(
                        {'name': cat_type}, {'lists': 1})
                elif cat_id:
                    returns = self._db.gc_applists.find(
                        {'id': cat_id}, {'lists': 1})
                else:
                    returns = []
                lists += [j for i in returns for j in i['lists']
                          if j['id'] > start]

        except Exception, e:
            print e

        return lists[:count] if len(lists) > 0 else []


gc_db = GameCenterMongodbStorage(
    'mongodb://' + settings.DOLPHINOP_DB['server'] + ':' + str(settings.DOLPHINOP_DB['port']))


@json_response
@require_GET
def Application(request):
    app_id = get_parameter_GET(
        request, 'app_id', required=False, convert_func=int)
    return gc_db.queryApplication(app_id) if app_id != '' else []


@json_response
@require_GET
def Search(request):
    keyword = get_parameter_GET(request, 'keyword', required=True)

    return gc_db.querySearch(keyword)


@json_response
@require_GET
def App_list(request):
    request_get = request.GET
    method = request_get.get('m', '')
    list_id = request_get.get('cid', 0)
    list_type = request_get.get('type', '')
    list_name = request_get.get('cname', '')
    start = request_get.get('start', 0)
    count = request_get.get('count', 20)

    return gc_db.queryAppList(method, start, count, list_id, list_type) if method else []


@json_response
@require_GET
def Category(request):
    return gc_db.queryCategory()


@json_response
@require_GET
def Subject(request):
    return gc_db.querySubject()


@json_response
@require_GET
def Banner(request):
    return gc_db.queryBanner()

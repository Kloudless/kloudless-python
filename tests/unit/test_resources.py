import json
import requests
import copy
import datetime
import pytz

from mock import MagicMock, patch, call
from requests.models import Response

import helpers
import kloudless
from kloudless.resources import Account, Folder, File

@helpers.configured_test
def test_account_list():
    resp = Response()
    resp._content = helpers.account_list.encode('utf-8')
    resp.encoding = 'utf-8'
    with patch('kloudless.resources.request') as mock_req:
        mock_req.return_value = resp
        accounts = Account().all()
        assert len(accounts) > 0
        assert all([isinstance(x, Account) for x in accounts])

@helpers.configured_test
def test_account_retrieve():
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        resp._content = helpers.account.encode('utf-8')
        resp.encoding = 'utf-8'
        mock_req.return_value = resp
        account_data = json.loads(helpers.account)
        account = Account().retrieve(account_data['id'])
        assert isinstance(account, Account)
        for attr in ['id', 'service', 'active', 'account']:
            assert account_data[attr] == getattr(account, attr)
        mock_req.assert_called_with(account._api_session.get,
                                    'accounts/%s' % account_data['id'],
                                    configuration=None,
                                    headers=None,
                                    params={})

@helpers.configured_test
def test_folder_contents():
    account = Account.create_from_data(json.loads(helpers.account))
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        resp._content = helpers.root_folder_contents.encode('utf-8')
        resp.encoding = 'utf-8'
        mock_req.return_value = resp
        folder = account.folders()
        contents = folder.contents(headers={'k': 'v'})
        assert len(contents) > 0
        assert all([(isinstance(x, Folder) or isinstance(x, File)) for x in contents])
        mock_req.assert_called_with(folder._api_session.get,
                                    ('accounts/%s/storage/folders/root/contents'
                                        % account.id),
                                    configuration=account._configuration,
                                    headers={'k': 'v'})

@helpers.configured_test
def test_folder_metadata():
    account = Account.create_from_data(json.loads(helpers.account))
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        resp._content = helpers.folder_data.encode('utf-8')
        resp.encoding = 'utf-8'
        mock_req.return_value = resp
        folder_data = json.loads(helpers.folder_data)
        folder = Folder.retrieve(id=folder_data['id'],
                                 parent_resource=account)
        assert isinstance(folder, Folder)
        for attr in ['id', 'name', 'type', 'size', 'account']:
            assert folder_data[attr] == getattr(folder, attr)
        mock_req.assert_called_with(Folder._api_session.get,
                                    ('accounts/%s/storage/folders/%s'
                                        % (account.id, folder_data['id'])),
                                    configuration=None,
                                    headers=None,
                                    params={})

@helpers.configured_test
def test_folder_creation():
    account = Account.create_from_data(json.loads(helpers.account))
    folder_data = json.loads(helpers.folder_data)
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        resp.status_code = 201
        resp._content = helpers.folder_data.encode('utf-8')
        resp.encoding = 'utf-8'
        mock_req.return_value = resp
        folder = Folder.create(parent_resource=account,
                               data={'name': "TestFolder",
                                     'parent_id': "root"})
        assert isinstance(folder, Folder)
        for attr in ['id', 'name', 'type', 'size', 'account']:
            assert folder_data[attr] == getattr(folder, attr)
        mock_req.assert_called_with(Folder._api_session.post,
                                    'accounts/%s/storage/folders' % account.id,
                                    configuration=None, params={},
                                    headers=None,
                                    data={'name': 'TestFolder',
                                          'parent_id': 'root'})

@helpers.configured_test
def test_folder_delete():
    account = Account.create_from_data(json.loads(helpers.account))
    folder_data = json.loads(helpers.folder_data)
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        resp.status_code = 204
        mock_req.resturn_value = resp
        folder = Folder.create_from_data(json.loads(helpers.folder_data),
                                         parent_resource=account)
        folder.delete()
        mock_req.assert_called_with(Folder._api_session.delete,
                                    ('accounts/%s/storage/folders/%s'
                                     % (account.id, folder_data['id'])),
                                    configuration=account._configuration,
                                    headers=None,
                                    params={})

@helpers.configured_test
def test_file_metadata():
    account = Account.create_from_data(json.loads(helpers.account))
    file_data = json.loads(helpers.file_data)
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        resp._content = helpers.file_data.encode('utf-8')
        resp.encoding = 'utf-8'
        mock_req.return_value = resp
        file_obj = File.retrieve(id=file_data['id'],
                                 parent_resource=account)
        assert isinstance(file_obj, File)
        for attr in ['id', 'name', 'type', 'size', 'account']:
            assert file_data[attr] == getattr(file_obj, attr)
        mock_req.assert_called_with(File._api_session.get,
                                    ('accounts/%s/storage/files/%s'
                                        % (account.id, file_data['id'])),
                                    configuration=None,
                                    headers=None,
                                    params={})

@helpers.configured_test
def test_file_contents():
    account = Account.create_from_data(json.loads(helpers.account))
    file_data = json.loads(helpers.file_data)
    file_obj = File.create_from_data(file_data, parent_resource=account)
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        resp._content = helpers.file_contents
        mock_req.return_value = resp
        file_contents = file_obj.contents()
        assert isinstance(file_contents, Response)
        mock_req.assert_called_with(file_obj._api_session.get,
                                    ('accounts/%s/storage/files/%s/contents'
                                        % (account.id, file_data['id'])),
                                    configuration=file_obj._configuration,
                                    headers=None,
                                    stream=True)

@helpers.configured_test
def test_file_delete():
    account = Account.create_from_data(json.loads(helpers.account))
    file_data = json.loads(helpers.file_data)
    file_obj = File.create_from_data(file_data, parent_resource=account)
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        resp.status_code = 204
        mock_req.return_value = resp
        file_obj.delete()
        mock_req.assert_called_with(file_obj._api_session.delete,
                                    ('accounts/%s/storage/files/%s'
                                        % (account.id, file_data['id'])),
                                    configuration=file_obj._configuration,
                                    headers=None,
                                    params={})

@helpers.configured_test
def test_file_upload():
    account = Account.create_from_data(json.loads(helpers.account))
    file_data = json.loads(helpers.file_data)
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        resp._content = helpers.file_data.encode('utf-8')
        resp.encoding = 'utf-8'
        mock_req.return_value = resp
        file_obj = File.create(parent_resource=account,
                               file_name=file_data['name'],
                               parent_id='root',
                               headers={'k': 'v'},
                               file_data=helpers.file_contents)
        assert isinstance(file_obj, File)
        for attr in ['id', 'name', 'type', 'size', 'account']:
            assert file_data[attr] == getattr(file_obj, attr)
        mock_req.assert_called_with(File._api_session.post,
                                    'accounts/%s/storage/files' % account.id,
                                    data=helpers.file_contents,
                                    headers={
                                        'k': 'v',
                                        'Content-Type':
                                            'application/octet-stream',
                                        'X-Kloudless-Metadata': json.dumps({
                                                'name': file_data['name'],
                                                'parent_id': 'root'})
                                    },
                                    params=None,
                                    configuration=None)

@helpers.configured_test
def test_file_update():
    account = Account.create_from_data(json.loads(helpers.account))
    file_data = json.loads(helpers.file_data)
    file_obj = File.create_from_data(file_data, parent_resource=account)
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        new_data = file_data.copy()
        new_data['name'] = 'NewFileName'
        resp._content = json.dumps(new_data).encode('utf-8')
        resp.encoding = 'utf-8'
        account_resp = Response()
        account_resp._content = helpers.account.encode('utf-8')
        account_resp.encoding = 'utf-8'
        mock_req.side_effect = (resp,account_resp)
        file_obj.name = 'NewFileName'
        file_obj.parent_id = 'root'
        file_obj.save()
        expected_calls = [
                          # This is updating the file
                          call(file_obj._api_session.patch,
                               'accounts/%s/storage/files/%s' % (account.id,
                                                         file_data['id']),
                               params={},
                               data={'name': u'NewFileName',
                                     'parent_id': 'root'},
                               headers=None,
                               configuration=file_obj._configuration),
                          # This is refreshing the parent resource
                          call(account._api_session.get,
                               'accounts/%s' % account.id,
                               headers=None,
                               configuration=account._configuration),
                         ]
        mock_req.assert_has_calls(expected_calls)

@helpers.configured_test
def test_file_copy():
    account = Account.create_from_data(json.loads(helpers.account))
    file_data = json.loads(helpers.file_data)
    file_obj = File.create_from_data(file_data, parent_resource=account)
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        new_data = file_data.copy()
        new_data['name'] = 'NewFileName'
        resp._content = json.dumps(new_data).encode('utf-8')
        resp.encoding = 'utf-8'
        account_resp = Response()
        account_resp._content = helpers.account
        mock_req.side_effect = (resp,account_resp)
        file_obj.copy_file(name='NewFileName', parent_id='root')
        expected_calls = [
                          # This is copying the file
                          call(file_obj._api_session.post,
                               'accounts/%s/storage/files/%s/copy' % (account.id,
                                                         file_data['id']),
                               data={'name': u'NewFileName',
                                     'parent_id': 'root'},
                               headers=None,
                               configuration=file_obj._configuration),
                         ]
        mock_req.assert_has_calls(expected_calls)


@helpers.configured_test
def test_file_property_list():
    account = Account.create_from_data(json.loads(helpers.account))
    file_data =  json.loads(helpers.file_data)
    file_obj = File.create_from_data(file_data, parent_resource=account)
    property_data = json.loads(helpers.property_data) 
    properties = property_data.get('properties')
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        resp._content = helpers.property_data.encode('utf-8')
        resp.encoding = 'utf-8'
        mock_req.return_value = resp
        properties_obj = kloudless.resources.Property.all(parent_resource=file_obj)
        assert properties_obj is not None
        props = properties_obj.get('properties')
        assert len(props) > 0
        index = 0
        for prop in props:
            for attr in ['key', 'value', 'created', 'modified']:
                assert prop.get(attr) == properties[index].get(attr)
            index += 1
        mock_req.assert_called_with(kloudless.resources.Property._api_session.get,
                'accounts/%s/storage/files/%s/properties' % (account['id'],
                    file_obj['id']),
                configuration=None,
                headers=None)


@helpers.configured_test
def test_file_property_patch():
    account = Account.create_from_data(json.loads(helpers.account))
    file_data =  json.loads(helpers.file_data)
    file_obj = File.create_from_data(file_data, parent_resource=account)
    property_data = json.loads(helpers.property_data)
    properties = property_data.get('properties')
    sorted(properties)
    new_properties = copy.deepcopy(properties)
    new_properties[0]['value'] = 'test update'
    # remove the second one
    new_properties.remove(new_properties[1])
    new_properties.append({
        'key':'newkey',
        'value': 'newvalue',
        'created': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'modified': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        })
    content = json.dumps(new_properties)
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        resp._content = content
        resp.encoding = 'utf-8'
        resp.status_code = 200
        mock_req.return_value = resp
        updated_properties = kloudless.resources.Property.update(
                parent_resource=file_obj,data=new_properties)
        assert updated_properties is not None
        assert len(updated_properties) == 2
        sorted(updated_properties)
        index = 0
        for prop in updated_properties:
            for attr in ['key', 'value', 'created', 'modified']:
                if attr == 'created' or attr == 'modified':
                    datetime_obj = datetime.datetime.strptime(
                            new_properties[index].get(attr),
                            '%Y-%m-%dT%H:%M:%S.%fZ')
                    datetime_obj_utc = datetime_obj.replace(
                            tzinfo=pytz.timezone('UTC'))
                    assert prop.get(attr) == datetime_obj_utc
                else:
                    assert prop.get(attr) == new_properties[index].get(attr)
            index += 1
        mock_req.asssert_called_with(kloudless.resources.Property._api_session.patch,
                'accounts/%s/storage/files/%s/properties' %
                (account['id'], file_obj['id']),
                configuration=file_obj._configuration,
                headers=None)

@helpers.configured_test
def test_file_property_delete():
    account = Account.create_from_data(json.loads(helpers.account))
    file_data =  json.loads(helpers.file_data)
    file_obj = File.create_from_data(file_data, parent_resource=account)
    with patch('kloudless.resources.request') as mock_req:
        resp = Response()
        resp.status_code = 204
        mock_req.return_value = resp
        deleted_properties = kloudless.resources.Property.delete_all(
                parent_resource=file_obj)
        assert deleted_properties is not None
        mock_req.assert_called_with(kloudless.resources.Property._api_session.delete,
                'accounts/%s/storage/files/%s/properties' % 
                (account['id'], file_obj['id']), configuration=None,
                headers=None)

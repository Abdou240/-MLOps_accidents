from fastapi.testclient import TestClient
from .main import app
import pytest

client = TestClient(app)

# For all: test response for correct and incorrect data

class TestAdmin:
	def test_retrain_model():
		assert client.post('/admin/model/retrain').status_code == 200
	
	def test_stats_model():

	def test_predict_model():

	def test_users_list():

	def test_users_add():

	def test_users_remove():

	def test_users_update():

class TestSuperUSer:
	def test_gen_stats():

	def test_stats_query():

class TestUser:
	def test_risky_locations():
		tests = []
		tests.append(client.get('/gen_user/risky_locations'))

	def test_query_location():

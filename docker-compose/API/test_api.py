from fastapi.testclient import TestClient
from .main import app
import pytest

client = TestClient(app)

class TestAdmin:
	def test_retrain_model():
		assert retrain_model() == True
	
	def test_stats_model():

	def test_predict_model():

	def test_users_list():

	def test_users_add():

	def test_users_remove():

	def test_users_update():
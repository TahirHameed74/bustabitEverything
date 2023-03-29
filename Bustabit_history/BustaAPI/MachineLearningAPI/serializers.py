from rest_framework import serializers
from . models import anomaly

class anomalySerializers(serializers.ModelSerializer):
	class Meta:
		model=anomaly
		fields='__all__'
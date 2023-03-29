from django.db import models

# Create your models here.
class anomaly(models.Model):
	file_name=models.CharField(max_length=256)
	timeseries_column_name=models.CharField(max_length=100)
	value_column_name=models.CharField(max_length=100)

	def __str__(self):
		return '{}, {}'.format(self.timeseries_column_name, self.value_column_name)
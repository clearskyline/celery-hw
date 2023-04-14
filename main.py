import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from celery.result import AsyncResult
from flask import Flask, jsonify, request

from celery import Celery
from flask.views import MethodView

from upscale import upscale_func


app_name = 'app'
app = Flask(app_name)
celery = Celery(
    app_name,
    backend='redis://localhost:6379/3',
    broker='redis://localhost:6379/4'
)


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask


@celery.task(queue='celery', name='upscale_photos')
def upscale_photos(path_1, path_2):
    result = upscale_func(path_1, path_2, 'EDSR_x2.pb')
    file_id = result.split("/")[-1]
    return file_id


class UpscaleData(MethodView):

    def get(self, task_id):
        task = AsyncResult(task_id, app=celery)
        target_file_name = f'files/{task.result}'
        return jsonify({'status': task.status,
                       'full_path': target_file_name,
                        'file_id': task.result})

    def post(self):
        json_data = request.json
        input_path = os.path.join('files', json_data['image_1'])
        output_path = os.path.join('files', json_data['image_2'])
        task = upscale_photos.delay(input_path, output_path)
        return jsonify({'task_id': task.id})


class ManageFiles(MethodView):

    def get(self, file_id):
        image_path = os.path.join('files', file_id)
        image = mpimg.imread(image_path)
        plt.imshow(image)
        plt.show()
        return jsonify({'result': 'image displayed'})


upscale_view = UpscaleData.as_view('upsc')
app.add_url_rule('/tasks/<string:task_id>/', view_func=upscale_view, methods=['GET'])
app.add_url_rule('/upscale/', view_func=upscale_view, methods=['POST'])

file_view = ManageFiles.as_view('upsc_files')
app.add_url_rule('/processed/<string:file_id>/', view_func=file_view, methods=['GET'])


if __name__ == '__main__':
    app.run()

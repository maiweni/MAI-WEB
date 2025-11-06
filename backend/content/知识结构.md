# 				mawen知识结构清单



## 一、云服务器租界（autodl）













## 二、大模型微调（LLM）



### 1、llmafactory微调教程

- clone项目

  ```
  git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git
  ```

- 搭建微调环境

  ```
  conda create -n llm python=3.10
  cd LLaMA-Factory
  pip install -e ".[torch,metrics]" --no-build-isolation -i https://pypi.tuna.tsinghua.edu.cn/simple
  
  ```

- 下载微调需要的模型

  ```
  #模型下载
  from modelscope import snapshot_download
  model_dir = snapshot_download('Qwen/Qwen2.5-7B-Instruct', local_dir='./qwen2.5_7b')
  ```

  ```Python
  python down_model.py
  ```

- 将配置文件复制到微调文件夹中

  ```
  mkdir qwen_sft
  cp -r examples/train_lora/llama3_lora_sft.yaml qwen_sft/qwen_train_lora_sft.yaml
  cp -r examples/merge_lora/llama3_lora_sft.yaml qwen_sft/qwen_merge_lora_sft.yaml
  ```

- 修改微调配置文件如下所示：

  ```
  ### model
  model_name_or_path: /root/autodl-tmp/LLaMA-Factory/qwen2.5_7b
  trust_remote_code: true
  
  ### method
  stage: sft
  do_train: true
  finetuning_type: lora
  lora_rank: 8
  lora_target: all
  
  ### dataset
  dataset: identity,alpaca_en_demo
  template: qwen
  cutoff_len: 2048
  max_samples: 10000000
  overwrite_cache: true
  preprocessing_num_workers: 16
  dataloader_num_workers: 4
  
  ### output
  output_dir: saves/qwen2.5_7b/lora/sft
  logging_steps: 10
  save_steps: 500
  plot_loss: true
  overwrite_output_dir: true
  save_only_model: false
  report_to: none  # choices: [none, wandb, tensorboard, swanlab, mlflow]
  
  ### train
  per_device_train_batch_size: 1
  gradient_accumulation_steps: 8
  learning_rate: 1.0e-4
  num_train_epochs: 3.0
  lr_scheduler_type: cosine
  warmup_ratio: 0.1
  bf16: true
  ddp_timeout: 180000000
  resume_from_checkpoint: null
  
  ### eval
  # eval_dataset: alpaca_en_demo
  # val_size: 0.1
  # per_device_eval_batch_size: 1
  # eval_strategy: steps
  # eval_steps: 500
  
  ```

- 开始训练

  ```
  llamafactory-cli train qwen_sft/qwen_train_lora_sft.yaml
  ```

- 模型融合

  ```
  ### Note: DO NOT use quantized model or quantization_bit when merging lora adapters
  
  ### model
  model_name_or_path: /root/autodl-tmp/LLaMA-Factory/qwen2.5_7b
  adapter_name_or_path: saves/qwen2.5_7b/lora/sft
  template: qwen
  trust_remote_code: true
  
  ### export
  export_dir: output/qwen2.5_7b_lora_sft
  export_size: 5
  export_device: cpu  # choices: [cpu, auto]
  export_legacy_format: false
  
  ```

  ```
  llamafactory-cli train qwen_sft/qwen_merge_lora_sft.yaml
  ```

- llamafactory api接口调用

  直接使用lora推理

  ```
  CUDA_VISIBLE_DEVICES=0 API_PORT=8000 llamafactory-cli api \
      --model_name_or_path /media/codingma/LLM/llama3/Meta-Llama-3-8B-Instruct \
      --adapter_name_or_path ./saves/LLaMA3-8B/lora/sft \
      --template llama3 \
      --finetuning_type lora
  ```

  使用vllm后端进行推理（禁用lora）

  ```
  CUDA_VISIBLE_DEVICES=0 API_PORT=8000 llamafactory-cli api \
      --model_name_or_path megred-model-path \
      --template llama3 \
      --infer_backend vllm \
      --vllm_enforce_eager
  ```

  实例代码如下：

  ```
  import os
  from openai import OpenAI
  from transformers.utils.versions import require_version
  
  require_version("openai>=1.5.0", "To fix: pip install openai>=1.5.0")
  
  if __name__ == '__main__':
      # change to your custom port
      port = 8000
      client = OpenAI(
          api_key="0",
          base_url="http://localhost:{}/v1".format(os.environ.get("API_PORT", 8000)),
      )
      messages = []
      messages.append({"role": "user", "content": "hello, where is USA"})
      result = client.chat.completions.create(messages=messages, model="test")
      print(result.choices[0].message)
  ```



### 2、ms-swift微调教程

- 安装环境，与llamafactory类似直接通过源码安装即可
- https://swift.readthedocs.io/zh-cn/latest/Instruction/%E9%A2%84%E8%AE%AD%E7%BB%83%E4%B8%8E%E5%BE%AE%E8%B0%83.html

















## 四、目标检测任务



### 1、yolov5系列目标检测

- 训练命令：

  ```
  python train.py  \
      --cfg models/yolov5s.yaml \
      --data data/Clothing_NanRaoCheng.yaml \
      --hyp data/hyps/hyp.scratch-hsv.yaml \
      --epochs 100 \
      --batch-size 16 \
      --img-size 640 \
      --project runs/train/ \
      --name Clothing_NanRaoCheng_20251009 \
      --weights yolov5s.pt \
      --device 1
  ```







### 2、yolov11系列目标检测









### 3、Dino目标检测

- dino介绍：

  ```
  dino是2022年的一篇论文，作用是万物检测，给出对应的文本描述，即可通过bert模型可以将文本转成向量，并与图像对齐，实现对目标的检测
  ```

- 项目地址：

  ```
  github链接：https://github.com/IDEA-Research/GroundingDINO
  ```

- 训练的项目地址

  ```
  https://github.com/longzw1997/Open-GroundingDino
  备注：
  训练的时候标签都是从0开始，否则会出现验证集精度非常低的情况
  ```

  





## 五、comfyui系列任务

### 1、文生图

- 部署comfyui
  - 通过autodl镜像部署，克隆comfyui，云绘工具箱，下载需要用到的模型，并启动comfyui，使用autodl远程工具打开comfyui界面。
  - 通过本地源码部署，
  - windows可以直接下载comfyui的客户端，直接安装



### 2、通过api完成comfyui的调用

- 在设置中打开comfyui的开发者模式

- 导出工作流的json文件（使用api）

- 使用下面的代码调用工作流

  ```
  import json
  import websocket  # NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
  import uuid
  import urllib.request
  import urllib.parse
  import random
  import os
  
  # 定义一个函数来显示GIF图片
  def show_gif(fname):
      import base64
      from IPython import display
      with open(fname, 'rb') as fd:
          b64 = base64.b64encode(fd.read()).decode('ascii')
      return display.HTML(f'<img src="data:image/gif;base64,{b64}" />')
  
  # 定义一个函数向服务器队列发送提示信息
  # 修改queue_prompt函数添加错误处理
  def queue_prompt(prompt):
      try:
          p = {"prompt": prompt, "client_id": client_id}
          data = json.dumps(p).encode('utf-8')
          req = urllib.request.Request(
              "http://{}/prompt".format(server_address), 
              data=data,
              headers={"Content-Type": "application/json"}
          )
          with urllib.request.urlopen(req) as response:
              return json.loads(response.read())
      except urllib.error.HTTPError as e:
          print(f"API Error: {e.code} {e.reason}")
          print(e.read().decode())  # 打印详细错误信息
          raise
  
  # 定义一个函数来获取图片
  def get_image(filename, subfolder, folder_type):
      data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
      url_values = urllib.parse.urlencode(data)
      with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
          return response.read()
  
  # 定义一个函数来获取历史记录
  def get_history(prompt_id):
      with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
          return json.loads(response.read())
  
  # 定义一个函数来获取图片，这涉及到监听WebSocket消息
  def get_images(ws, prompt):
      prompt_id = queue_prompt(prompt)['prompt_id']
      print('prompt')
      print(prompt)
      print('prompt_id:{}'.format(prompt_id))
      output_images = {}
      while True:
          out = ws.recv()
          if isinstance(out, str):
              message = json.loads(out)
              if message['type'] == 'executing':
                  data = message['data']
                  if data['node'] is None and data['prompt_id'] == prompt_id:
                      print('执行完成')
                      break  # 执行完成
          else:
              continue  # 预览为二进制数据
  
      history = get_history(prompt_id)[prompt_id]
      print(history)
      for o in history['outputs']:
          for node_id in history['outputs']:
              node_output = history['outputs'][node_id]
              # 图片分支
              if 'images' in node_output:
                  images_output = []
                  for image in node_output['images']:
                      image_data = get_image(image['filename'], image['subfolder'], image['type'])
                      images_output.append(image_data)
                  output_images[node_id] = images_output
              # 视频分支
              if 'videos' in node_output:
                  videos_output = []
                  for video in node_output['videos']:
                      video_data = get_image(video['filename'], video['subfolder'], video['type'])
                      videos_output.append(video_data)
                  output_images[node_id] = videos_output
  
      print('获取图片完成')
      print(output_images)
      return output_images
  
  # 解析工作流并获取图片
  def parse_worflow(ws, prompt, seed, workflowfile):
      workflowfile = workflowfile
      print('workflowfile:'+workflowfile)
      with open(workflowfile, 'r', encoding="utf-8") as workflow_api_txt2gif_file:
          prompt_data = json.load(workflow_api_txt2gif_file)
          # 设置文本提示
          prompt_data["6"]["inputs"]["text"] = prompt
  
          return get_images(ws, prompt_data)
  
  # 生成图像并显示
  def generate_clip(prompt, seed, workflowfile, idx):
      print('seed:'+str(seed))
      ws = websocket.WebSocket()
      ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
      images = parse_worflow(ws, prompt, seed, workflowfile)
  
      for node_id in images:
          for image_data in images[node_id]:
              from datetime import datetime
  
              # 获取当前时间，并格式化为 YYYYMMDDHHMMSS 的格式
              timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
  
              # 使用格式化的时间戳在文件名中
              GIF_LOCATION = "{}/{}_{}_{}.png".format(SageMaker_ComfyUI, idx, seed, timestamp)
  
              print('GIF_LOCATION:'+GIF_LOCATION)
              with open(GIF_LOCATION, "wb") as binary_file:
                  # 写入二进制文件
                  binary_file.write(image_data)
  
              show_gif(GIF_LOCATION)
  
              print("{} DONE!!!".format(GIF_LOCATION))
  
  
  import pandas as pd
  
  
  # Example of reading from a CSV file
  def read_prompts_from_csv(csv_file_path):
      df = pd.read_excel(csv_file_path)
      return df['prompt'].tolist()
  
  # 在执行generate_clip前添加
  if not os.path.exists('output'):
      os.makedirs('output')
  
  # Execute the main function
  if __name__ == "__main__":
      # 设置工作目录和项目相关的路径
      WORKING_DIR = 'output'
      SageMaker_ComfyUI = WORKING_DIR
      workflowfile = 'q2.json'
      COMFYUI_ENDPOINT = '127.0.0.1:6006'
  
      server_address = COMFYUI_ENDPOINT
      client_id = str(uuid.uuid4())  # 生成一个唯一的客户端ID
  
      seed = 15465856
      idx = 1
      prompt = '丽江宝藏城市美展现得淋漓尽致！画面中，传统中式建筑错落有致，色彩鲜艳的飞檐斗拱，尽显古韵。宏伟的金塔在阳光下闪耀，玉龙雪山巍峨耸立，让人感受到它的壮丽与神秘。彩虹横跨天际，给整个画面增添了梦幻色彩。丽江古城的水车缓缓转动，旁边的鲜花饼散发着诱人香气，还有娇艳的花朵点缀其间。得月楼、束河古镇等标志性地点一一呈现，每一处都充满故事。丽江城市插画中式建筑旅游打卡地'
      generate_clip(prompt, seed, workflowfile, idx)
      # csv_file_path = 'prompt.xlsx'
      # prompts = read_prompts_from_csv(csv_file_path)
  
      # idx = 1
      # for prompt in prompts:
      #     generate_clip(prompt, seed, workflowfile, idx)
      #     idx += 1
  ```

  









## 六、minerU部署与使用

### 1、minerU部署

- minerU下载，这里使用源码安装，其实也可以直接安装包

  ```
  git clone https://github.com/opendatalab/MinerU.git
  cd MinerU
  python -m venv venv 
  source venv/bin/activate
  pip install -e .[core] -i https://mirrors.aliyun.com/pypi/simple
  ```

  通过上述命令即可完成minerU的安装

### 2、minerU的使用

- minerU通过命令行使用

  ```
  mineru -p <input_path> -o <output_path>
  ```

  注意：在初次使用的时候，minerU会从huggingface中下载模型，因此这里需要设置huggingface镜像。

  ```
  export HF_ENDPOINT=https://hf-mirror.com
  ```

  

## 七、qwen code配置

```
export OPENAI_API_KEY='sk-5b87682537b148b6a0f92bcd74334736'
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export OPENAI_MODEL=qwen3-coder-plus
```









## 八、知识图谱






















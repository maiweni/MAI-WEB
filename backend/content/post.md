# 多模态嵌入模型使用

## 一、目的

​	为了能够在RAG的时候，对图片进行召回，或者是实现以图搜图等操作，需要对图片的语义进行编码，实现将图片转成向量，完成向量空间的比较。这里我们使用的是多模态嵌入模型：谷歌的SigLIP模型。



## 二、使用流程

- 模型下载

  该模型在huggingface与modelscope模型平台上都有，因此，我们选择从modelscope上进行下载，模型id为：google/siglip2-base-patch16-512，下载代码如下：

  ```
  #模型下载
  from modelscope import snapshot_download
  model_dir = snapshot_download('google/siglip2-base-patch16-512'，local_dir='./siglip2-base-patch16-512')
  ```

- 模型使用流程

  为了能够实现并发操作，我们这里使用fastapi暴露接口，并通过transformers的AutoModel.from_pretrained函数完成模型的部署。

  - 模型初始化

    模型初始化，使用fastapi的startup装饰器完成在fastapi服务启动的时候完成模型的加载，代码如下：

    ```
    @app.on_event("startup")
    async def _startup() -> None:
        await _service.ensure_loaded()
    
    
    async def ensure_loaded(self) -> None:
        if self._model is not None:
            return
        async with self._load_lock:
            if self._model is not None:
                return
            await asyncio.get_running_loop().run_in_executor(None, self._load_model)
    
    def _load_model(self) -> None:
        processor = AutoProcessor.from_pretrained(self.model_id)
        model = AutoModel.from_pretrained(self.model_id, torch_dtype=self.dtype)
        model.to(self.device)
        model.eval()
        self._processor = processor
        self._model = model
    ```

    通过上述代码即可完成模型的初始化操作，并将模型加载到显存中。

  - 模型嵌入

    模型嵌入部分可以使用fastapi创建接口，使用装饰器如@app.post("/embed", response_model=EmbedResponse)，代码如下所示：

    ```
    服务接口
    @app.post("/embed", response_model=EmbedResponse)
    async def embed(
        payload: ItemInput,
        service: Annotated[SiglipService, Depends(get_service)],
    ) -> EmbedResponse:
        # Run heavy work in a thread so FastAPI's event loop stays responsive.
        return await run_in_threadpool(service.embed, payload)
       
    
    嵌入方法
    def embed(self, payload: ItemInput) -> EmbedResponse:
        image = decode_image(payload.image_base64)
        vectors = self._encode(image, payload.text)
        fused_list = vectors.fused.tolist()
        return EmbedResponse(
            fused_embedding=fused_list,
            image_embedding=vectors.image.tolist(),
            text_embedding=vectors.text.tolist(),
            dimension=len(fused_list),
            model_id=self.model_id,
        )
        
    
    图像转base64
    def decode_image(image_b64: str) -> Image.Image:
        # If a file path is provided, read bytes directly (convenient when caller has local images).
        if os.path.exists(image_b64):
            try:
                with open(image_b64, "rb") as f:
                    raw = f.read()
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unable to read image file: {exc}",
                ) from exc
        else:
            try:
                raw = base64.b64decode(image_b64, validate=True)
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid base64 image payload or missing file: {exc}",
                ) from exc
    
        try:
            image = Image.open(io.BytesIO(raw))
            image = image.convert("RGB")
            return image
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to read image: {exc}",
            ) from exc
            
    
    
    将文本与图像转化成向量嵌入
    def _encode(self, image: Image.Image, text: str) -> EmbeddingVectors:
        if self._processor is None or self._model is None:
            raise RuntimeError("Model not loaded. Call ensure_loaded() first.")
    
        inputs = self._processor(
            text=[text],
            images=[image],
            padding=True,
            return_tensors="pt",
        )
        inputs = {k: v.to(self.device, non_blocking=True) for k, v in inputs.items()}
    
        with torch.no_grad():
            outputs = self._model(**inputs)
    
        image_embeds = F.normalize(outputs.image_embeds, p=2, dim=-1)
        text_embeds = F.normalize(outputs.text_embeds, p=2, dim=-1)
    
        fused = F.normalize((image_embeds + text_embeds) / 2.0, p=2, dim=-1)
    
        return EmbeddingVectors(
            image=image_embeds[0].detach().cpu(),
            text=text_embeds[0].detach().cpu(),
            fused=fused[0].detach().cpu(),
        )
    
    
    ```

    


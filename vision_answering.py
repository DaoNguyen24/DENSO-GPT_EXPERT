import base64
import requests
import fitz
import os
from openai import OpenAI
from Retrive_weaviate import List_of_meta_data


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def get_images(file_path, save_file, page, count):
    doc = fitz.open(file_path)
    page = doc.load_page(int(page))  # number of page
    pix = page.get_pixmap()
    pix.save(save_file + str(count) + '.jpg')
    doc.close()
    return save_file + str(count) + '.jpg'

def answer_image(query, metadatas: list[dict]):
    client = OpenAI(api_key="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")

    qs = f"""
    bạn là một kĩ sư,
    Từ những ảnh cung cấp, chỉ trả lời câu hỏi mà tôi đưa ra, chính xác mã lỗi của câu hỏi
    câu hỏi: {query}
    """
    
    list_path = []
    for i, meta in enumerate(metadatas):
        path = get_images(meta['source'], 'images/', meta['page'], i)
        list_path.append(path)
        
    images = [encode_image(val) for val in list_path]
    
    response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    temperature=0.5,
    messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": qs,
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{images[0]}",
              },
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{images[1]}",
              },
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{images[2]}",
                },
            },
          ],
        }
      ],
      max_tokens=300,
    )
    return response.choices[0].message.content
 
if __name__ == "__main__":
    query = "Làm thế nào để sửa lỗi int3170 trên máy CNC1"
    metadatas = List_of_meta_data(query=query)
    answer = answer_image(query, metadatas)
    print(answer)

def Response(query):
    metadatas = List_of_meta_data(query=query)
    list_of_metadata = []
    for meta in metadatas:
        source = {
            "source": meta["source"],
            "page": meta["page"]
        }
        list_of_metadata.append(source)
    answer = answer_image(query, metadatas)
    return answer,list_of_metadata
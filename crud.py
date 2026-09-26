from db import Session
from sqlalchemy import select
import models
import datetime

def get_material_by_hash(file_hash):
    with Session() as session:
        data = session.execute(
            select(models.Material).where(models.Material.content_hash == file_hash)
        ).scalars().first()
    return data

def add_material(file_name,file_hash):
    material = models.Material(name=file_name,content_hash=file_hash)
    with Session() as session:
        session.add(material)
        session.commit()
        material_id = material.id
    
    return material_id # to pass to add_chunks()

def add_chunks(chunks,material_id):
    with Session() as session:
        rows = []
        for position, doc in enumerate(chunks):
            rows.append(
                models.Chunk(
                content=doc.page_content,
                material_id=material_id,
                position=position+1,
                headings=' > '.join(doc.metadata.values())
                ))
        session.add_all(rows)
        material = session.get(
            models.Material, material_id
        )
        material.last_processed = datetime.datetime.now(datetime.timezone.utc) # processed time is adding now ot when we add material.
        session.commit()
        

if __name__ == '__main__':
    d = get_material_by_hash('12345678896575675654564645354574635')
    
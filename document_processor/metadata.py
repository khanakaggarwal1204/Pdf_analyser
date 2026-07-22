def add_metadata(chunks, source):
    chunk_data=[]
    for i, chunk in enumerate(chunks):
        chunk_data.append({
            "id":i+1,
            "source":source,
            "text":chunk
        })
    return chunk_data
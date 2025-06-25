from preprocess import extract_features
sample_document = {
    "URL": "http://localhost:8080/tienda1/publico/caracteristicas.jsp?id=1 HTTP/1.1",
    "Method": "GET",
    "content": "",
    "classification": 0
}

features = extract_features(sample_document)

print("Extracted Features:", features)

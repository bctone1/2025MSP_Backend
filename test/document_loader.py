import os
from langchain_service.document_loaders.file_loader import load_document
from pprint import pprint

if __name__ == "__main__":
    test_files = [
        "./test_documents/File_Loader_Test.txt",
        "./test_documents/File_Loader_Test.pdf",
        "./test_documents/File_Loader_Test.docx",
        "./test_documents/File_Loader_Test.csv"
    ]

    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                print(f"\n=== {file_path} 로드 테스트 ===")
                documents = load_document(file_path)
                print(f"✅ {file_path} 로드 성공! 문서 개수: {len(documents)}")
                pprint(documents[:2])  # 첫 2개 문서 미리보기
            except Exception as e:
                print(f"❌ {file_path} 로드 실패: {e}")
        else:
            print(f"⚠️ {file_path} 파일이 존재하지 않습니다. 테스트를 위해 준비해주세요.")
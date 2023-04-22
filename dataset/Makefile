TEST_FILE_NAME=test
TEST_FILE_EXTENSION=.mp3

sanitize:
	python3 sanitizer.py

scrappe:
	python3 scrapper.py

checksum:
	md5 final_dataset.tar.gz

remove_silence:
	python3 ./modules/silence_remover.py 3 $(TEST_FILE_NAME)$(TEST_FILE_EXTENSION) 

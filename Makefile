
install: build install_program


build:
	python3 -m py_compile include/*.py
	python3 -m py_compile *.py

clean:
	find . -name \*.pyc -type f -delete
	find . -name __pycache__ -type d -delete


install_program:
	mkdir -p /opt/strack/
	cp -r * /opt/strack/
	chown root:root /opt/strack -R
	find /opt/strack/ -type d -exec chmod u=rwx,g=rx,o= {} \;
	find /opt/strack/ -type f -exec chmod u=rw,g=r,o= {} \;
	find /opt/strack/ -type f -name '*.py' -exec chmod u=rwx,g=rx,o= {} \;
	chmod o+rx /opt

uninstall:
	rm -rf /opt/strack



Здесь представлен вариант развертывания через Ansible.
Для работы нужны 4 виртуальные машины - на первой будет запускаться ansible (там в одной директории лежат: конфиг, инвентарь, плейбук и .env), который будет разворачивать:
- базу данных на 2й ВМ;
- базу данных для репликации на 3й ВМ;
- тг-бота на 4й ВМ. 

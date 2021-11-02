import subprocess as sp
import uuid


class ManageConf:
    def __init__(self, config):
        self.domain = config['domain']
        self.static_path = config['static_path'] if 'static_path' in config else ''
        self.redirect_url = config['redirect_url'] if 'redirect_url' in config else ''

        self.enableSSL = True if 'enableSSL' in config and config['enableSSL'] == 1 else False
        self.forceSSL = True if 'forceSSL' in config and config['forceSSL'] == 1 and self.enableSSL else False
        self.websocket = True if 'websocket' in config and config['websocket'] == 1 else False
        self.type = config['type'] if 'type' in config else 'static'
        self.HSTS = True if 'HSTS' in config and config['HSTS'] == 1 and self.enableSSL else False
        self.http2 = True if 'http2' in config and config['http2'] == 1 and self.enableSSL else False
        self.block_exploit = True if 'block_exploit' in config and config['block_exploit'] == 1 else False
        self.ips = config['ips'] if 'ips' in config else []
        self.ssl_cert_path = config['ssl_cert_path'] if 'ssl_cert_path' in config else ''
        self.ssl_key_path = config['ssl_key_path'] if 'ssl_key_path' in config else ''

        self.unique_upstream = f'sd_load_balancer_{self.domain.replace(".","_")}_{uuid.uuid4().hex}'
        self.newLine = '\n'
        self.tab = '\t'

    def __get_http(self):
        if (self.forceSSL):
            return f'{self.newLine}server {{{self.newLine}{self.tab}listen 80;{self.newLine}{self.tab}server_name {self.domain.strip()};{self.newLine}{self.tab}return 301 https://$host$request_uri;'
        else:
            partA = f'\n\n\t{self.__get_common_exploit()}\n' if self.block_exploit and not self.forceSSL else ''

            return f'{self.newLine}server {{{self.newLine}{self.tab}listen 80;{self.newLine}{self.tab}server_name {self.domain.strip()};{self.newLine}{self.tab}{partA}'

    def __get_common_exploit(self):
        try:
            common_exploits = open(f"./config/common_exploit.sd", "r").read()
            return common_exploits
        except:
            return ''

    def __get_ssl(self):
        partB = ' http2' if self.http2 else ''
        partC = '\n\t\tadd_header Strict-Transport-Security "max-age=31536000; preload" always;\n' if self.HSTS else ''
        partD = f'\n\n\t{self.__get_common_exploit()}\n' if self.block_exploit else ''

        return f'''server {{
        listen 443 ssl{partB};{partC}
        server_name {self.domain.strip()};\n

        ssl_certificate {self.ssl_cert_path};
        ssl_certificate_key {self.ssl_key_path};

        ssl_stapling on;
        ssl_stapling_verify on;

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        add_header Strict-Transport-Security max-age=15768000;\n
    '''

    def __get_location(self):

        xForwaard = '\n\n''''
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Server $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
                ''''\n'

        websocket_support = '''
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 80;''''\n'

        partA = f'{self.newLine}{self.tab}{self.tab}add_header Strict-Transport-Security "max-age=31536000; preload" always;{self.newLine}' if self.HSTS else ''
        if (self.type == 'static' and not self.websocket):
            return f'{self.newLine}{self.tab}location / {{{partA}{xForwaard}{self.newLine}{self.tab}{self.tab}root {self.static_path};{self.newLine}{self.tab}}}'

        if (self.type == 'static' and self.websocket):
            return f'{self.newLine}{self.tab}location / {{{partA}{xForwaard}{self.newLine}{websocket_support}{self.newLine}{self.tab}{self.tab}root {self.static_path};{self.newLine}{self.tab}}}'

        elif (self.type == 'redirect'):
            return f'{self.newLine}{self.tab}location / {{{self.newLine}{self.tab}{self.tab}return 301 http://{self.redirect_url};{self.newLine}{self.tab}}}'

        elif (self.type == 'reverse_proxy' and not self.websocket):
            return f'{self.newLine}{self.tab}location / {{{partA}{xForwaard}{self.newLine}{self.tab}{self.tab}proxy_pass http://{self.unique_upstream};{self.newLine}{self.tab}}}'
        elif (self.type == 'reverse_proxy' and self.websocket):
            return f'{self.newLine}{self.tab}location / {{{partA}{xForwaard}{self.newLine}{self.tab}{self.tab}proxy_pass http://{self.unique_upstream};{self.newLine}{websocket_support}{self.newLine}{self.tab}}}'

    def __get_load_balancer(self):
        partA = f'upstream {self.unique_upstream} {{'
        partB = '\n'
        for ip in self.ips:
            partB = partB + \
                f"{self.tab}server {ip['ip']}:{ip['port']};{self.newLine}" if 'port' in ip else partB+'\t'+'server ' + ip['ip']+';\n'
        partC = '}\n\n'
        return partA + partB + partC

    def createConf(self):
        if self.type == 'redirect':
            self.enableSSL = self.forceSSL = self.websocket = False
        partA = self.__get_load_balancer() if self.type == 'reverse_proxy' else ''
        partB = self.__get_ssl() + self.__get_location() + '\n}' + self.__get_http() + \
            '\n}' if self.enableSSL and self.forceSSL else self.__get_ssl() + self.__get_location() + '\n}' if self.enableSSL else False
        partC = self.__get_http() + self.__get_location() + '\n}' if not self.forceSSL else ''
        confFile = open(f"../data/nginx_conf/{self.domain}.conf", "w")
        confFile.write(partA+partB+partC if partB else partA+partC)
        confFile.close()

    @staticmethod
    def reload_nginx():
        reload_status = sp.getoutput('nginx -s reload')
        if 'signal process started' in reload_status:
            return True
        return

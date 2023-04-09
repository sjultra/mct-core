import configparser
import os
from singleton_decorator import singleton
from cdktf import TerraformVariable, NamedCloudWorkspace

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError

AppContext = { "excludeStackIdFromLogicalIds" : True, "allowSepCharsInLogicalIds": True }

CONFIG_SPEC = {
    'AwsProvider': {
        'region': '',
        'access_key': '',
        'secret_key': ''
    },
    'CloudBackend': {
        'hostname': '',
        'organization': '',
        'workspaces': '',
        'token': ''
    },
}

class AzureKeyVault():
    _credentials = None
    _client = None
    _enabled = True

    def __init__(self):
        self._credentials = {
            self.__class__.__name__: {
                'client_id': '',
                'client_secret': '',
                'tenant_id': '',
                'vault_url': ''
            }
        }

    def init_credentials(self, config):
        self._enabled = self._check_creadentials(config)

        self._init_client()

        return self._enabled

    def get_secret(self, secret_name):
        secret_name = self._change_secret_name(secret_name)
        if self._enabled:
            try:
                print("Retrieving secret value for: ", secret_name)
                secret_value = self._client.get_secret(secret_name).value
                return secret_value
            except ResourceNotFoundError:
                print(f"Unable to retrieve value for secret '{secret_name}'")
                return ''
        else:
            return ''

    def _change_secret_name(self, secret):
        return secret.replace('_', '-')

    def _check_creadentials(self, config):
        if self._check_config(config):
            return True
        elif self._check_env():
            return True
        else:
            return False

    def _init_client(self):
        creds = self._credentials[self.__class__.__name__]

        credential = ClientSecretCredential(
            tenant_id=creds['tenant_id'],
            client_id=creds['client_id'''],
            client_secret=creds['client_secret']
        )

        self._client = SecretClient(vault_url=creds['vault_url'], credential=credential)


    def _check_config(self, config):
        if self.__class__.__name__ in config:
            for key in self._credentials[self.__class__.__name__]:
                if key in config[self.__class__.__name__] and config[self.__class__.__name__][key] != '':
                    self._credentials[self.__class__.__name__][key] = config[self.__class__.__name__][key]
                else:
                    return False
        else:
            return False

        print("Found credentials in config.ini")
        return True


    def _check_env(self):
        for key in self._credentials[self.__class__.__name__]:
            full_key = self.__class__.__name__ + '_' + key
            if full_key in os.environ:
                self._credentials[self.__class__.__name__][key] = os.environ[full_key]
            else:
                return False
        print("Found credentials in environment variables")
        return True

class ConfigProvider():
    _config = None
    _secret_provider = None
    _secret_provider_enabled = False

    def __init__(self, secret_provider=None):
        self._init_config()
        self._secret_provider = secret_provider

        if self._secret_provider is not None:
            self._secret_provider_enabled =  self._secret_provider.init_credentials(self._config)
            self._config._sections.update(self._secret_provider._credentials)

    def _init_config(self):
        self._config = configparser.ConfigParser()

        if not os.path.exists('config.ini'):
            with open('config.ini', 'w') as f:
                f.write('')

        self._config.read('config.ini')

    def write_config(self):
        with open('config.ini', 'w') as f:
            self._config.write(f)

    def get_config(self, spec):
        if spec in self._config and self._config[spec].keys() == CONFIG_SPEC[spec].keys():
            return self._config._sections[spec]
        else:
            self._config._sections.update({spec: CONFIG_SPEC[spec]})
            return self._config._sections[spec]

    def get_backend_config(self, spec):
        backendConfig = self.get_config(spec).copy()
        backendConfig['workspaces'] = NamedCloudWorkspace(backendConfig['workspaces'])
        return backendConfig

    def get_secret_values(self):
        if self._secret_provider_enabled:
            for section in self._config._sections:
                for key in self._config._sections[section]:
                    if self._config._sections[section][key] == '':
                        secret_name = section + '_' + key
                        self._config._sections[section][key] = self._secret_provider.get_secret(secret_name)
        else:
            return None


    def scan_app(self, app):
        variables = []

        for child in app.node.children[0].node.children:
            if isinstance(child, TerraformVariable):
                variables.append(child.friendly_unique_id)

        if len(variables) > 0:
            if 'TerraformVariable' not in self._config._sections:
                self._config._sections.update( {
                    'TerraformVariable': {}
                })

            for variable in variables:
                if variable not in self._config._sections['TerraformVariable']:
                    self._config._sections['TerraformVariable'].update({variable: ''})


@singleton
class MCT():
    app = None
    _config = None

    def __init__(self, app, secret_provider=None):
        self.app = app
        self._config = ConfigProvider(secret_provider)

    def run(self, command):
        if command == 'synth':
            self.app.synth()
        elif command == 'generateconfig':
            self._config.scan_app(self.app)
            self._config.write_config()
        elif command == 'getsecrets':
            self._config.scan_app(self.app)
            self._config.get_secret_values()
            self._config.write_config()

    def get_config(self, spec):
        return self._config.get_config(spec)

    def get_backend_config(self, spec):
        return self._config.get_backend_config(spec)

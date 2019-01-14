from fabric.api import *
import json


env.token = '***'
env.api = 'https://api.digitalocean.com/v2/'
env.http_headers = "-H 'Content-Type: application/json' -H 'Authorization: Bearer {0}'".format(env.token)
env.user = 'root'
env.key_filename = './id_rsa'


@task
def account():
    """Get User Information"""
    _jdump(local("curl -X GET {0} \"{1}account\"\n".format(env.http_headers, env.api), capture=True))


@task
def keys():
    """List all Keys"""
    _jdump(local("curl -X GET {0} \"{1}account/keys\"\n".format(env.http_headers, env.api), capture=True))


@task
def addkey():
    """Create a new Key"""
    public_key = local("cat ./id_rsa.pub", capture=True)
    request_body = "-d '{{\"name\":\"Default\",\"public_key\":\"{0}\"}}'".format(public_key)
    _jdump(local("curl -X POST {0} {1} \"{2}account/keys\"\n".
                 format(env.http_headers, request_body, env.api), capture=True))


@task
def regions():
    """List All Droplets"""
    _jdump(local("curl -X GET {0} \"{1}regions\"\n".format(env.http_headers, env.api), capture=True))


@task
def images():
    """List All Droplets"""
    _jdump(local("curl -X GET {0} \"{1}images?page=1&per_page=100\"\n".format(env.http_headers, env.api), capture=True))


@task
def droplets():
    """List All Droplets"""
    _jdump(local("curl -X GET {0} \"{1}droplets\"\n".format(env.http_headers, env.api), capture=True))


@task
def create_a_droplet(name="Woo"):
    """Create a new Droplet"""
    ssh_key_id = _get_key("Default")
    #ssh_key_id = 605624
    request_body = "-d '{0}'".format(json.dumps(
        {"name": name, "region": "sgp1", "size": "1gb", "image": "ubuntu-14-04-x64", "ssh_keys": [ssh_key_id]}))
    _jdump(local("curl -X POST {0} {1} \"{2}droplets\"\n".format(env.http_headers, request_body, env.api),
                 capture=True))


@task
def delete_the_droplet(name="Woo"):
    """Delete the given droplet"""
    with settings(warn_only=True):
        local("curl -X DELETE {0} \"{1}droplets/{2}\"\n".format(env.http_headers, env.api, _get_droplet_id(name)))
    local("ssh-keygen -f \"$HOME/.ssh/known_hosts\" -R {0}".format(env.host))


@task
def initial_config():
    """ Configure the remote host to run torrent service. """
    print("Executing on %s as %s" % (env.host, env.user))
    sudo('uname -a')
    sudo('apt-get update -q')
    sudo('apt-get upgrade -q -y')
    sudo('apt-get install -q -y pwgen transmission-cli transmission-common transmission-daemon')
    with settings(warn_only=True):
        sudo('service transmission-daemon stop')
    sudo('cp /etc/transmission-daemon/settings.json /etc/transmission-daemon/settings.orign')
    default_settings = json.loads(sudo('cat /etc/transmission-daemon/settings.json', quiet=True))
    overlay_settings = json.loads(local('cat ./settings.json', capture=True))
    for (i, item) in overlay_settings.items():
        default_settings[i] = item
    default_settings['rpc-password'] = sudo('pwgen -c -n -1 6')
    print json.dumps(default_settings, indent=4, sort_keys=True)
    print "|=================================|"
    print "|=== rpc-password: {0} ========|".format(default_settings['rpc-password'])
    print "|=================================|"
    f = open('./final_settings.json', 'w')
    json.dump(default_settings, f, indent=4, sort_keys=True)
    f.close()
    put('./final_settings.json', '/tmp/settings.json', mode=0644)
    sudo('cat /tmp/settings.json > /etc/transmission-daemon/settings.json')
    sudo('service transmission-daemon start')
    print "\n\n|= web access:  http://transmission:{0}@{1}:{2}/  =|\n\n".\
        format(default_settings['rpc-password'], env.host, default_settings['rpc-port'])
    key_file_path = local("readlink -e {0}".format(env.key_filename), capture=True)
    print "probably your scp command - after downloads - looks like this:"
    print "\tscp -i {0} -r root@{1}:/var/lib/transmission-daemon/downloads/ ./".\
        format(key_file_path, env.host)



@task
def set_host(name="Woo"):
    r = local("curl -X GET {0} \"{1}droplets\"\n".format(env.http_headers, env.api), capture=True)
    r = json.loads(r)
    for droplet in r['droplets']:
        if droplet['name'] == name:
            print "Droplet founded: [{0}]:{1}".format(droplet['name'], droplet['id'])
            print "Droplet founded: [{0}]:{1}".format(droplet['name'], droplet['id'])
            print "           host: {0}".format(droplet['networks']['v4'][0]['ip_address'])
            env.hosts = [droplet['networks']['v4'][0]['ip_address']]
            return droplet['networks']['v4'][0]['ip_address']
    abort("Droplet is missing.")


@task
def _get_droplet_id(name="Woo"):
    r = local("curl -X GET {0} \"{1}droplets\"\n".format(env.http_headers, env.api), capture=True)
    r = json.loads(r)
    for droplet in r['droplets']:
        if droplet['name'] == name:
            print "Droplet founded: [{0}]:{1}".format(droplet['name'], droplet['id'])
            print "Droplet founded: [{0}]:{1}".format(droplet['name'], droplet['id'])
            print "           host: {0}".format(droplet['networks']['v4'][0]['ip_address'])
            return droplet['id']
    abort("Droplet is missing.")


def _get_key(name="Default"):
    r = local("curl -X GET {0} \"{1}account/keys\"\n".format(env.http_headers, env.api), capture=True)
    r = json.loads(r)
    for ssh_key in r['ssh_keys']:
        if ssh_key['name'] == name:
            print "Founded ssh key: [{0}]:{1}".format(ssh_key['name'], ssh_key['id'])
            return ssh_key['id']
    abort("SSH key is missing.")


def _jdump(s):
    print json.dumps(
        json.loads(s), indent=4)

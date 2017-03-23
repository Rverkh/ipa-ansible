#!/usr/bin/python
# -*- coding: utf-8 -*-

# import module snippets
from ansible.module_utils.basic import *
import imp

def main():
	arg_spec = dict(
		hostip=dict(required=True),
		hostname=dict(required=True),
		force_dns_zone=dict(required=False, Default=False, choices=[True, False]),
		ipahost=dict(required=True),
		ipalogin=dict(required=True),
		ipapass=dict(required=True)
	)
	module = AnsibleModule(argument_spec=arg_spec, supports_check_mode=True)
	foo = imp.load_source('ipahttp', '/root/ipahttp1.py')
	
	params = module.params

	hostip = params['hostip']
	hostname = params['hostname']
	force_dns_zone = params['force_dns_zone']
	ipahost = params['ipahost']
	ipalogin = params['ipalogin']
	ipapass = params['ipapass']
	dns_zone=hostname.split(".",1)[1]
	dns_name=hostname.split(".",1)[0]
	ipa = foo.ipa(ipahost)


	login_result  = ipa.login(ipalogin, ipapass)
	if (login_result.status_code != 200):
		module.fail_json(msg='Fail to login to IPA')

	ipa_result = ipa.dnszone_find(dns_zone)
	if (ipa_result['error'] != None):
		module.fail_json(msg=ipa_result['error'])
	if (ipa_result['result']['count'] == 0 ) & (force_dns_zone == False):
		module.fail_json(msg='Dns zone not exist and no force create parameter set')
	if ( ipa_result['result']['count'] == 0 ) & (force_dns_zone == True):
		ipa_result=ipa.dnszone_add(dns_zone)
		if (ipa_result['error'] != None):
			module.fail_json(msg = ipa_result['error'])
	


	ipa_result = ipa.host_find(hostname)
	if (ipa_result['error'] != None):
		module.fail_json(msg=ipa_result['error'])
	if (ipa_result['result']['count'] == 1):
		module.fail_json(msg='Host already exist')

	ipa_result=ipa.host_add(hostname)
	if (ipa_result['error'] != None):
		module.fail_json(msg=ipa_result['error'])




	ipa_result = ipa.dnsrecord_find(dns_zone,dns_name, True)
	if (ipa_result['error'] != None):
		module.fail_json(msg=ipa_result['error'])
	if (ipa_result['result']['count'] == 1):
		module.fail_json(msg='DNS zone already exist')
	ipa_result=ipa.dnsrecord_add(dns_zone,dns_name,hostip)
	if (ipa_result['error'] != None):
		module.fail_json(msg=ipa_result['error'])
		
		
	
	



	changed=True	
	module.exit_json(changed=changed, msg="All action complete")




if __name__ == '__main__':
	main()

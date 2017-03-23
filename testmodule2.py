#!/usr/bin/env python


from ansible.plugins.action import ActionBase
import pprint


#from importlib.machinery import SourceFileLoader

#foo = SourceFileLoader("ipahttp", "/root/ipahttp1.py").load_module()
import imp
foo = imp.load_source('ipahttp', '/root/ipahttp1.py')
import platform



class ActionModule(ActionBase):

	def run(self, tmp=None, task_vars=None):
		print(platform.python_version())
		if task_vars is None:
			task_vars = dict()
		result = super(ActionModule, self).run(tmp, task_vars)
		host = 'ipa.example.test'
		passwd = '12345678'
		user = "Admin"
		login_attempt=0
		ipa = foo.ipa(host)
		login_result  = ipa.login(user, passwd)
#		if (login_result.status_code != 200):
#			while (login_result.status_code != 200) & (login_attempt < 5):
#				login_result  = ipa.login(user, passwd)
#				login_attempt = login_attempt +1
		if (login_result.status_code != 200):
			print(passwd)
			print(login_result.headers)
			result['Fail_reason'] = "Fail to login to IPA"
			result['IPA_response_code'] = login_result.status_code
			result['failed'] = True
			return result
		args = self._task.args.copy()
		hostname=args['hostname']
		zbxip=args['hostip']
		dns_zone=hostname.split(".",1)[1]
		dns_name=hostname.split(".",1)[0]





		#Find and add dns zone if not exist
		ipa_result = ipa.dnszone_find(dns_zone)
		if (ipa_result['error'] != None):
			result['Fail_reason']=ipa_result['error']
			result['failed'] = True
			return result
			
		if(ipa_result['result']['count'] == 1):
			result['dns_status']="dns zone exist"
		else:
			ipa_result=ipa.dnszone_add(dns_zone)
			if (ipa_result['error'] != None):
				result['Fail_reason']=ipa_result['error']
				result['failed'] = True
				return result
			else:
				result['dns_status']="Dns zone added"





		#Find and add host if not exist
		ipa_result =   ipa.host_find(hostname)
		if (ipa_result['error'] != None):
			result['Fail_reason']=ipa_result['error']
			result['failed'] = True
			return result

		if (ipa_result['result']['count'] == 1):
			result['Fail_reason']="Host already exist"
			result['failed'] = True
			return result


		result['host_status']="Host not exist. Create host"
		ipa_result=ipa.host_add(hostname)

		if (ipa_result['error'] != None):
			result['Fail_reason']=ipa_result['error']
			result['failed'] = True
			return result
		else:
			result['host_status']="Host created"


		
		#Find and create arecord
		ipa_result = ipa.dnsrecord_find(dns_zone,dns_name, True)
		if (ipa_result['error'] != None):
			result['Fail_reason']=ipa_result['error']
			result['failed'] = True
			return result

		if (ipa_result['result']['count'] == 1):
			result['Fail_reason']="DNS record already exist"
			result['failed'] = True
			return result

		ipa_result=ipa.dnsrecord_add(dns_zone,dns_name,zbxip)
		if (ipa_result['error'] != None):
			result['Fail_reason']=ipa_result['error']
			result['failed'] = True
			return result
		else:
			result['dns_record_status']="DNS record created"



		result['failed'] = False
		return result

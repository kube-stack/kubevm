/**
 * Copyright (2019, ) Institute of Software, Chinese Academy of Sciences
 */
package com.github.kube.ha;

import java.io.File;
import java.io.FileInputStream;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.yaml.snakeyaml.Yaml;

import com.github.kube.ha.watchers.VirtualMachineWatcher;
import com.github.kubesys.kubernetes.ExtendedKubernetesClient;

import io.fabric8.kubernetes.client.Config;
import io.fabric8.kubernetes.client.ConfigBuilder;

/**
 * @author shizhonghao17@otcaix.iscas.ac.cn
 * @author yangchen18@otcaix.iscas.ac.cn
 * @author wuheng@otcaix.iscas.ac.cn
 * @since Wed May 01 17:26:22 CST 2019
 * 
 * https://www.json2yaml.com/
 * http://www.bejson.com/xml2json/
 * 
 * debug at runWatch method of io.fabric8.kubernetes.client.dsl.internal.WatchConnectionManager
 **/
public class KubevirtVMHA {
	
	protected final static Logger m_logger = Logger.getLogger(KubevirtVMHA.class.getName());

	public final static String TOKEN              = "/etc/kubernetes/admin.conf";
	
	protected final ExtendedKubernetesClient client;
	
	public KubevirtVMHA() throws Exception {
		this(TOKEN);
	}
	
	@SuppressWarnings("rawtypes")
	public KubevirtVMHA(String token) throws Exception {
		super();
		Map<String, Object> map = new Yaml().load(
				new FileInputStream(new File(token)));
		@SuppressWarnings("unchecked")
		Map<String, Map<String, Object>> clusdata = (Map<String, Map<String, Object>>)
												((List) map.get("clusters")).get(0);
		@SuppressWarnings("unchecked")
		Map<String, Map<String, Object>> userdata = (Map<String, Map<String, Object>>)
												((List) map.get("users")).get(0);
		Config config = new ConfigBuilder()
				.withApiVersion("v1")
				.withCaCertData((String) clusdata.get("cluster").get("certificate-authority-data"))
				.withClientCertData((String) userdata.get("user").get("client-certificate-data"))
				.withClientKeyData((String) userdata.get("user").get("client-key-data"))
				.withMasterUrl((String) clusdata.get("cluster").get("server"))
				.build();
		client = new ExtendedKubernetesClient(config);
	}
	
	public void start() {
		client.watchVirtualMachines(new VirtualMachineWatcher(client));
	}
	
	public static void main(String[] args) throws Exception {
		m_logger.log(Level.INFO, "Start VirtualMachineWatcher");
		m_logger.log(Level.INFO, "Start VirtualMachineImageWatcher");
		m_logger.log(Level.INFO, "Start VirtualMachineDiskWatcher");
		m_logger.log(Level.INFO, "Start VirtualMachineUITDiskWatcher");
		m_logger.log(Level.INFO, "Start VirtualMachineSnapshotWatcher");
		KubevirtVMHA scheduler = new KubevirtVMHA();
		try {
			scheduler.start();
		} catch (Exception ex) {
			m_logger.log(Level.SEVERE, "Fail to start controller:" + ex);
		}
	}

}
# DLS4E Technical specification

## Compatibility matrix

|Product|Features and elements|Ubuntu|CentOS|RedHat|Windows|
|:----------------------------------:|:--------:|:------:|:------:|:------:|:-------:|
|***Vanila Kubernetes***             |Core K8sCluster, flanneld, tiller, kubernetes-dashboard |**+** *(offline for AILabs)*|**+**|**+**|**-**|
|***Kubernetes Cluster Installer***  |...|**+**|**+**|**+**|**-**|
|***Kubernetes Features Installer*** |docker-registry, dls-gui, elasticsearch, fluentd, samba-dls, crds(Experiment/Template/Run), redsocks |**+**|**+**|**+**|**+**|
|***DLS CLI***                       |...|**+**|**+**|**+**|**+**|

## OS Dictionary
- Ubuntu - 16.04 and above
- CentOs - 
- RedHat - 
- Windows -

## Initial Users

<table width="100%">
  <tr>
    <th> Product </th>
    <th> Users </th>
  </tr>
  <tr>
    <td> Vanilla Kubernetes </td>
    <td> cluster-admin </td>
  </tr>
  <tr>
    <td> Kubernetes Cluster Installer </td>
    <td> </td>
  </tr>
  <tr>
    <td> Kubernetes Features Installer </td>
    <td> </td>
  </tr>
    
</table>

## Initial Roles

<table width="100%">
  <tr>
    <th> Product </th>
    <th> Roles </th>
  </tr>
  <tr>
    <td> Vanilla Kubernetes </td>
    <td> cluster-admin </td>
  </tr>
  <tr>
    <td> Kubernetes Cluster Installer </td>
    <td> dls-common-access </td>
  </tr>
  <tr>
    <td> Kubernetes Features Installer </td>
    <td> dls4e-full-access, dls4e-read-only </td>
  </tr>
    
</table>

## User definitions

<b> cluster-admin </b>
The user is defined by the clusterrolebindings described below:

<table width="100%">
  <tr>
    <td><b>Kind:</b></td>
    <td colspan=2>clusterrolebinding</td>
  </tr>
  <tr>
    <td><b>Name:</b></td>
    <td colspan=2>cluster-admin-cluster-admin</td>
  </tr>
  <tr>
    <td><b>Labels:</b></td>
    <td colspan=2> </td>
  </tr>
  <tr>
    <td><b>Annotations:</b></td>
    <td colspan=2> </td>
  </tr>
  <tr>
    <td colspan=3><b>Role:</b></td>
  </tr>
  <tr>
    <td><b>Kind:</b></td>
    <td colspan=2> ClusterRole</td>
  </tr>
  <tr>
    <td><b>Name:</b></td>
    <td colspan=2>cluster-admin </td>
  </tr>
  <tr>
    <td colspan=3><b>Subjects:</b> </td>
   <tr>
     <td>Kind</td>
     <td>Name</td>
     <td>Namespace</td>
  </tr>
  <tr>
    <td>ServiceAccount </td>
    <td>cluster-admin</td>
    <td>auth</td>    
  </tr>
</table>


<table width="100%">
  <tr>
    <td><b>Kind:</b></td>
    <td colspan=2>clusterrolebinding</td>
  </tr>
  <tr>
    <td><b>Name:</b></td>
    <td colspan=2>cluster-admin-dls-common-access</td>
  </tr>
  <tr>
    <td><b>Labels:</b></td>
    <td colspan=2> </td>
  </tr>
  <tr>
    <td><b>Annotations:</b></td>
    <td colspan=2> </td>
  </tr>
  <tr>
    <td colspan=3><b>Role:</b></td>
  </tr>
  <tr>
    <td><b>Kind:</b></td>
    <td colspan=2> ClusterRole</td>
  </tr>
  <tr>
    <td><b>Name:</b></td>
    <td colspan=2>dls-common-access </td>
  </tr>
  <tr>
    <td colspan=3><b>Subjects:</b> </td>
   <tr>
     <td>Kind</td>
     <td>Name</td>
     <td>Namespace</td>
  </tr>
  <tr>
    <td>ServiceAccount </td>
    <td>cluster-admin</td>
    <td>auth</td>    
  </tr>
</table>

## Roles
<b> cluster-admin</b>
<table width="100%">
  <tr>
    <td colspan=2><b>Kind:</b></td>
    <td colspan=2>clusterrole</td>
  </tr>
  <tr>
    <td colspan=2><b>Name:</b></td>
    <td colspan=2>cluster-admin</td>
  </tr>
  <tr>
    <td colspan=2><b>Labels:</b></td>
    <td colspan=2>kubernetes.io/bootstrapping=rbac-defaults</td>
  </tr>
  <tr>
    <td colspan=2><b>Annotations:</b></td>
    <td colspan=2>rbac.authorization.kubernetes.io/autoupdate=true</td>
  </tr>
  <tr>
    <td colspan=4><b>PolicyRule:</b> </td>
   <tr>
     <td>Resources</td>
     <td>Non-Resource URLs</td>
     <td>Resource Names</td>
     <td>Verbs</td>
  </tr>
  <tr>
    <td> </td>
    <td>[*] </td>
    <td>[] </td>    
    <td>[*] </td>    
  </tr>
  <tr>
    <td>*.* </td>
    <td>[] </td>
    <td>[] </td>    
    <td>[*] </td>    
  </tr>

</table>

<b> dls-common-access</b>
<table width="100%">
  <tr>
    <td colspan=2><b>Kind:</b></td>
    <td colspan=2>clusterrole</td>
  </tr>
  <tr>
    <td colspan=2><b>Name:</b></td>
    <td colspan=2>dls-common-access</td>
  </tr>
  <tr>
    <td colspan=2><b>Labels:</b></td>
    <td colspan=2> </td>
  </tr>
  <tr>
    <td colspan=2><b>Annotations: </b></td>
    <td colspan=2> </td>
  </tr>
  <tr>
    <td colspan=4><b>PolicyRule:</b> </td>
   <tr>
     <td>Resources</td>
     <td>Non-Resource URLs</td>
     <td>Resource Names</td>
     <td>Verbs</td>
  </tr>
  <tr>
    <td>namespaces.* </td>
    <td> </td>
    <td>[namespaces] </td>    
    <td>[get watch list delete] </td>    
  </tr>
</table>

<b> dls4e-full-access</b>
<table width="100%">
  <tr>
    <td colspan=2><b>Kind:</b></td>
    <td colspan=2>clusterrole</td>
  </tr>
  <tr>
    <td colspan=2><b>Name:</b></td>
    <td colspan=2>dls4e-access</td>
  </tr>
  <tr>
    <td colspan=2><b>Labels:</b></td>
    <td colspan=2>app: {{ .Release.Name }}<br>
				  chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}<br>
				  release: {{ .Release.Name }}<br>
				  heritage: {{ .Release.Service }}<br>
				  *values given here are set up helm during installation of a chart</td>
  </tr>
  <tr>
    <td colspan=2><b>Annotations: </b></td>
    <td colspan=2> </td>
  </tr>
  <tr>
    <td colspan=4><b>PolicyRule:</b> </td>
   <tr>
     <td>Resources</td>
     <td>Non-Resource URLs</td>
     <td>Resource Names</td>
     <td>Verbs</td>
  </tr>
  <tr>
    <td>experiments</td>
    <td> </td>
    <td> </td>    
    <td>[create get watch list delete] </td>    
  </tr>
  <tr>
    <td>runs</td>
    <td> </td>
    <td> </td>    
    <td>[create get watch list delete] </td>    
  </tr>
</table>

<b> dls4e-read-only</b>
<table width="100%">
  <tr>
    <td colspan=2><b>Kind:</b></td>
    <td colspan=2>clusterrole</td>
  </tr>
  <tr>
    <td colspan=2><b>Name:</b></td>
    <td colspan=2>dls4e-access</td>
  </tr>
  <tr>
    <td colspan=2><b>Labels:</b></td>
    <td colspan=2>app: {{ .Release.Name }}<br>
				  chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}<br>
				  release: {{ .Release.Name }}<br>
				  heritage: {{ .Release.Service }}<br>
				  *values given here are set up helm during installation of a chart</td>
  </tr>
  <tr>
    <td colspan=2><b>Annotations: </b></td>
    <td colspan=2> </td>
  </tr>
  <tr>
    <td colspan=4><b>PolicyRule:</b> </td>
   <tr>
     <td>Resources</td>
     <td>Non-Resource URLs</td>
     <td>Resource Names</td>
     <td>Verbs</td>
  </tr>
  <tr>
    <td>experiments</td>
    <td> </td>
    <td> </td>    
    <td>[get watch list] </td>    
  </tr>
  <tr>
    <td>runs</td>
    <td> </td>
    <td> </td>    
    <td>[get watch list] </td>    
  </tr>
</table>

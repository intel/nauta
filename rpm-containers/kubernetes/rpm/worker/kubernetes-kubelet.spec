Summary: NAUTA Kubernetes Kubelet v%{_nauta_version} package
Name: nauta-kubernetes-kubelet
Version: %{_nauta_version}
Release: %{_nauta_release}
License: Apache-2.0
Group: Tools
SOURCE0 : kubernetes-server-linux-amd64.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

Requires: nauta-commons

Requires: iptables >= 1.4.21
Requires: nauta-cni-plugins >= 0.7.1
Requires: socat
Requires: util-linux
Requires: ethtool
Requires: iproute
Requires: ebtables

%define  debug_package %{nil}

%description
%{summary}

%prep
%setup -q -n kubernetes

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

mkdir -p %{buildroot}/opt/nauta/kubernetes
cp -a server/bin/kubelet %{buildroot}/opt/nauta/kubernetes/kubelet

%clean
rm -rf %{buildroot}


%files
%defattr(0755,root,root,-)
/opt/nauta/kubernetes/kubelet

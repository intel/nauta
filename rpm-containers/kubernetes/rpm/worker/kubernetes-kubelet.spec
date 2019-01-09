Summary: DLS4E Kubernetes Kubelet v%{_dls4e_version} package
Name: dls4e-kubernetes-kubelet
Version: %{_dls4e_version}
Release: %{_dls4e_release}
License: Apache-2.0
Group: Tools
SOURCE0 : kubernetes-server-linux-amd64.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

Requires: dls4e-commons

Requires: iptables >= 1.4.21
Requires: dls4e-cni-plugins >= 0.7.1
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

mkdir -p %{buildroot}/opt/dls4e/kubernetes
cp -a server/bin/kubelet %{buildroot}/opt/dls4e/kubernetes/kubelet


%clean
rm -rf %{buildroot}


%files
%defattr(0755,root,root,-)
/opt/dls4e/kubernetes/kubelet

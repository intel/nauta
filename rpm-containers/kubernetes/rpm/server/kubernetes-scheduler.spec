Summary: NAUTA Kubernetes Scheduler v%{_nauta_version} package
Name: nauta-kubernetes-scheduler
Version: %{_nauta_version}
Release: %{_nauta_release}
License: Apache-2.0
Group: Tools
SOURCE0 : kubernetes/server/kubernetes-server-linux-amd64.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

Requires: nauta-commons

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
cp -a server/bin/kube-scheduler %{buildroot}/opt/nauta/kubernetes/kube-scheduler

%clean
rm -rf %{buildroot}


%files
%defattr(0755,root,root,-)
/opt/nauta/kubernetes/kube-scheduler

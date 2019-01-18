Summary: NAUTA Kubernetes Kubectl v%{_nauta_version} package
Name: nauta-kubernetes-kubectl
Version: %{_nauta_version}
Release: %{_nauta_release}
License: Apache-2.0
Group: Tools
SOURCE0 : kubernetes.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

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

mkdir -p %{buildroot}%{_bindir}/kubernetes
cp -a kubectl %{buildroot}%{_bindir}/kubectl


%clean
rm -rf %{buildroot}


%files
%defattr(0755,root,root,-)
%{_bindir}/kubectl

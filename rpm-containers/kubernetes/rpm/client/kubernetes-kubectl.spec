Summary: DLS4E Kubernetes Kubectl v%{_dls4e_version} package
Name: dls4e-kubernetes-kubectl
Version: %{_dls4e_version}
Release: %{_dls4e_release}
License: Apache-2.0
Group: Tools
SOURCE0 : kubernetes-client-linux-amd64.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%define  debug_package %{nil}

%description
%{summary}

%prep
# Empty section.

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

mkdir -p %{buildroot}%{_bindir}/kubernetes
cp -a ../kubernetes/platforms/linux/amd64/kubectl %{buildroot}%{_bindir}

%clean
rm -rf %{buildroot}


%files
%defattr(0755,root,root,-)
%{_bindir}/kubectl

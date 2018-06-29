Summary: DLS4E Kubernetes Helm v%{_dls4e_version} package
Name: dls4e-helm
Version: %{_dls4e_version}
Release: %{_dls4e_release}
License: Apache-2.0
Group: Tools
SOURCE0 : helm.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%define  debug_package %{nil}

%description
%{summary}

%prep
%setup -q -n helm

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

mkdir -p %{buildroot}%{_bindir}
cp -a helm %{buildroot}%{_bindir}/helm


%clean
rm -rf %{buildroot}


%files
%defattr(0755,root,root,-)
%{_bindir}/helm

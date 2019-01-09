Summary: DLS4E Kubernetes CNI %{_dls4e_version} package
Name: dls4e-cni-plugins
Version: %{_dls4e_version}
Release: %{_dls4e_release}
License: Apache-2.0
Group: Tools
SOURCE0 : cni-plugins.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%define  debug_package %{nil}

%description
%{summary}

%prep
cd /root/rpmbuild/BUILD
rm -rf cni-plugins
mkdir cni-plugins
gzip -dc /root/rpmbuild/SOURCES/cni-plugins.tar.gz | tar -xvvf - -C cni-plugins
if [ $? -ne 0 ]; then
  exit $?
fi
cd cni-plugins
chown -R root.root .
chmod -R a+rX,g-w,o-w .

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

mkdir -p %{buildroot}/opt/dls4e/cni-plugins
cp -a cni-plugins/* %{buildroot}/opt/dls4e/cni-plugins/

%clean
rm -rf %{buildroot}


%files
%defattr(0755,root,root,-)
/opt/dls4e/cni-plugins/*

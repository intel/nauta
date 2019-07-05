Summary: NAUTA Precompiled pip python v%{_nauta_version} package
Name: nauta-pip-repository
Version: %{_nauta_version}
Release: %{_nauta_release}
License: Apache-2.0
Group: Tools
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%define  debug_package %{nil}

%description
%{summary}

%prep

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

mkdir -p %{buildroot}/opt/nauta/pip
pip wheel --no-binary=:all: ansible==2.7.9 pip==18.1 virtualenv==16.0.0 \
    setuptools==40.8.0 wheel==0.31.1 \
    docker==3.4.0 pyOpenSSL==17.5.0 \
    -w %{buildroot}/opt/nauta/pip/

exit 0
%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
/opt/nauta/pip/*

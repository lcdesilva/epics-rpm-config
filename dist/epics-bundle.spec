Name:           epics-bundle
Version:        7.0.8_0.0.0
Release:        2%{?dist}
Summary:        EPICS Base and Modules bundle

License:        BSD-3-Clause
URL:            https://github.com/NSLS2/rhel8-epics-config
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python3 boost-devel cmake gcc gcc-c++ giflib-devel git
BuildRequires:  libraw1394 libtirpc-devel libusb-devel libusbx-devel
BuildRequires:  libXext-devel libxml2-devel libXt-devel libXtst-devel
BuildRequires:  make motif-devel net-snmp-devel pcre-devel perl-devel
BuildRequires:  pkgconf re2c readline-devel rpcgen tar wget zeromq-devel
BuildRequires:  git-rpm-tools
Requires:       bash boost giflib libraw1394 libtirpc
Requires:       libusb libusbx libXext libxml2 libXt libXtst
Requires:       motif net-snmp-libs pcre perl re2c readline rpcgen zeromq

BuildArch:      x86_64

# Prevent rpmbuild from smart-generating dependencies list
AutoReq:        no

# Prevent rpmbuild from auto-mangling executable shebangs
%undefine __brp_mangle_shebangs

%description
EPICS base and modules bundle packaged as RPM.

%prep
%autosetup

# This starts in rpmbuildtree/BUILD/epics-bundle-...
%build
# %%configure
# %%make_build
if [ ! -d %{_topdir}/INSTALL/epics ]; then
    mkdir -p %{_topdir}/INSTALL

    # Handle the submodule which is not included by git archive
    cp -r %{_topdir}/../installSynApps/* %{_builddir}/%{name}-%{version}/installSynApps/.

    cd %{_builddir}/%{name}-%{version}/installSynApps
    python3 -u installCLI.py -y -c .. -b %{_builddir} -i %{_topdir}/INSTALL -p -f

    cd %{_topdir}/INSTALL
    mv EPICS_* epics
    cd epics
    patch -p1 < %{_builddir}/%{name}-%{version}/dist/makeBaseApp-basepath.patch
    patch -p1 < %{_builddir}/%{name}-%{version}/dist/disable-debug.patch

    # Blanket-fix any missing permissions
    chmod u+w -R %{_topdir}/INSTALL
fi

# This starts in rpmbuildtree/BUILDROOT
%install
# Ignore invalid rpaths in EPICS build
export QA_RPATHS=$[ 0x0001 | 0x0002 ]

# Clean up any old stuff
rm -rf %{buildroot}

# Populate /usr/lib64/epics
mkdir -p %{buildroot}/usr/lib64/epics
#cd %{_topdir}/INSTALL/epics
cp -r %{_topdir}/INSTALL/epics/* %{buildroot}/usr/lib64/epics/.

# Drop select binaries in /usr/bin
mkdir -p %{buildroot}/usr/bin
install %{_topdir}/INSTALL/epics/bin/linux-x86_64/{caget,cainfo,camonitor,caput,caRepeater,casw,pvget,pvinfo,pvmonitor,pvput,pvlist,edm,medm,msi} %{buildroot}/usr/bin/
install %{_topdir}/INSTALL/epics/bin/linux-x86_64/makeBaseApp.pl %{buildroot}/usr/bin/makeBaseApp

# Drop ld.so.conf file to point at EPICS libs
mkdir -p %{buildroot}/etc/ld.so.conf.d
cp %{_builddir}/%{name}-%{version}/dist/epics-bundle-x86_64.conf %{buildroot}/etc/ld.so.conf.d/.

# Create a symlink: /usr/lib/epics -> /usr/lib64/epics
mkdir -p %{buildroot}/usr/lib
ln -s /usr/lib64/epics %{buildroot}/usr/lib/epics

# %%make_install

%files
%dir /usr/lib64/epics
/usr/lib64/epics/*
/usr/lib/epics
/usr/bin/*
/etc/ld.so.conf.d/*
# Use lib64 instead of lib - TBD
#/lib64/*

%changelog
* Tue Apr 04 2023 Derbenev, Anton <aderbenev@bnl.gov> - 7.0.5_0.0.0-2
- Added git-rpm-tools in BuildRequires as the Makefile uses it
- Added LICENSE and adjusted .spec for it

* Wed Feb 15 2023 Derbenev, Anton <aderbenev@bnl.gov> - 7.0.5_0.0.0-1
- Removed jpeg libs, no longer needed after ADUVC driver rework
- Squashed revision bumpspecs
- Now using install for executables, not cp
- Makefile reviewed for git-mrt-tools compatibility
- Fixed the previously forgotten files section
- Change install location to lib64, now creating a symlink from lib
- Moved chmod fix in the build section, added more comments
- Updated URL
- Fixed wrong paths, added few comments
- Now using macroed paths instead of relative ones for clarity
- Now using builddir for patch and conf files
- Updated install and build sections for git-rpm-tools compatibility
- Changed the version number to follow the new scheme

* Tue Jan 31 2023 Derbenev, Anton <aderbenev@bnl.gov> - 0.1-9
- Revise specfile dir naming, sources and patches handling for git-mrt-tools compatibility

* Tue Jan 31 2023 Derbenev, Anton <aderbenev@bnl.gov> - 0.1-8
- Update Requires and BuildRequires

* Fri Mar 04 2022 Jakub Wlodek <jwlodek@bnl.gov> - 0.1-7
- Include autosave and areaDetector common iocBoot files

* Fri Jun 25 2021 Jakub Wlodek <jwlodek@bnl.gov> - 0.1-6
- Adding ezca and EzcaScan extension modules

* Tue May 18 2021 Jakub Wlodek <jwlodek@bnl.gov> - 0.1-5
- Adding optics module

* Thu May 06 2021 Anton Derbenev <aderbenev@bnl.gov> - 0.1-4
- Package rename to epics-bundle

* Mon May 3 2021 Anton Derbenev <aderbenev@bnl.gov> - 0.1-3
- Performing the source build during rpm build

* Tue Apr 27 2021 Anton Derbenev <aderbenev@bnl.gov> - 0.1-2
- Smarter installation and makeBaseApp patch

* Fri Apr 16 2021 Anton Derbenev <aderbenev@bnl.gov> - 0.1-1
- Initial relase of RPM

%global shortname PWRF-PWPS 
%global ver 3.7.1
%?altcc_init

Name:           %{shortname}%{?altcc_pkg_suffix}
Version:        %{ver}
Release:        1%{?dist}
Summary:        Polar WRF Model and WPS tools

License:        Public Domain
URL:            http://www.wrf-model.org/
Source0:        http://www2.mmm.ucar.edu/wrf/src/WRFV%{version}.TAR.gz
#This was created using the configure script and then modifying the 
#result
Source1:        configure.wrf-gfortran
Source2:        configure.wrf-pgf
Source3:        configure.wrf-intel
Source4:        wrf.module.in
Source5:        PWRF.3.7.1.tar.gz
Source10:       http://www2.mmm.ucar.edu/wrf/src/WPSV%{version}.TAR.gz
#This was created using the configure script and then modifying the
#result
Source11:       configure.wps-gfortran
Source12:       configure.wps-pgf
Source13:       configure.wps-intel
Source20:       setupwrf
# Fix linking against netcdf
Patch2:         WRF-WPS-netcdf.patch

BuildRequires:  tcsh
BuildRequires:  m4
%if !0%{?altcc}
BuildRequires:  gcc-gfortran
%endif
BuildRequires:  hdf%{?altcc_cc_dep_suffix}-devel
BuildRequires:  jasper-devel
BuildRequires:  libpng-devel
BuildRequires:  ncl%{?altcc_cc_dep_suffix}-devel
BuildRequires:  netcdf-fortran%{?altcc_dep_suffix}-devel
BuildRequires:  numactl-devel
BuildRequires:  time

%description
Polar WRF/WPS build.  They need to be built together which is why we have one
srpm.


%package -n PWRF%{?altcc_pkg_suffix}
Summary:        WRF Model
%{?altcc_reqmodules}
%{?altcc_provide:%altcc_provide -n PWRF}

%description -n PWRF%{?altcc_pkg_suffix}
Polar WRF Model.


%package -n PWPS%{?altcc_pkg_suffix}
Summary:        Polar WPS Tools
%{?altcc_provide:%altcc_provide -n PWPS}

%description -n PWPS%{?altcc_pkg_suffix}
Polar WPS Tools.


%prep
%setup -q -c -a 10
# Install PWRF files
find -name \*.PWRF%{version} | while read f
do
  name=${f/.PWRF%{version}/}
  cp -p $f WRFV3/${name}
done
%patch2 -p1 -b .netcdf
pushd WRFV3
[ -z "${COMPILER_NAME}" ] && export COMPILER_NAME=gfortran
cp %{_sourcedir}/configure.wrf-${COMPILER_NAME} configure.wrf
%if 0%{?rhel} && 0%{?rhel} <= 7
# Need gcc >= 4.10 for ieee_intrinsic
[ -z "$FC" ]  &&
  sed -i -e '/^ARCH_LOCAL/s/$/ -DNO_IEEE_MODULE/' configure.wrf
%endif
popd
pushd WPS
cp %{_sourcedir}/configure.wps-${COMPILER_NAME} configure.wps
popd


%build
%{?altcc:module load hdf ncl netcdf}
# This is set by the openmpi module and interferes with the build
unset MPI_LIB
if [ -n "${NETCDF_HOME}" ]; then
  export NETCDF=${NETCDF_HOME}
else
  export NETCDF=/usr
fi
export JASPERINC=/usr/include/jasper
export JASPERLIB=/usr/%{_lib}
export J=$(echo %{?_smp_mflags} | sed 's/-j/-j /')
pushd WRFV3
./compile em_real
popd
pushd WPS
./compile
# To explicitly compile plotfmt and plotgrids
./compile util
popd


%install
pushd WRFV3
mkdir -p %{buildroot}%{_bindir}
cp -a main/*.exe %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/WRFV3/test
cp -a run %{buildroot}%{_datadir}/WRFV3
rm %{buildroot}%{_datadir}/WRFV3/run/*.exe \
   %{buildroot}%{_datadir}/WRFV3/run/namelist.input
cp -a test/em_real %{buildroot}%{_datadir}/WRFV3/test
rm %{buildroot}%{_datadir}/WRFV3/test/em_real/*.exe
popd
pushd WPS
cp -a */src/*.exe %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/WRFV3/{geogrid,metgrid}
cp -a geogrid/*TBL* geogrid/gribmap.txt %{buildroot}%{_datadir}/WRFV3/geogrid
cp -a metgrid/*TBL* metgrid/gribmap.txt %{buildroot}%{_datadir}/WRFV3/metgrid
popd
sed -e s,@DATADIR@,%{_datadir},g < %SOURCE20 > %{buildroot}%{_bindir}/setupwrf
chmod +x %{buildroot}%{_bindir}/setupwrf

%{?altcc:%altcc_writemodule %SOURCE4}


%files -n PWRF%{?altcc_pkg_suffix}
#doc
%{?altcc:%altcc_files -m %{_bindir} %{_datadir}}
%{_bindir}/ndown.exe
# Temporarily removed
#{_bindir}/nup.exe
%{_bindir}/tc.exe
%{_bindir}/real.exe
%{_bindir}/wrf.exe
%{_bindir}/setupwrf
%dir %{_datadir}/WRFV3
%{_datadir}/WRFV3/run/
%{_datadir}/WRFV3/test/


%files -n PWPS%{?altcc_pkg_suffix}
#doc
%{?altcc:%altcc_files %{_bindir} %{_datadir}}
%{_bindir}/avg_tsfc.exe
%{_bindir}/calc_ecmwf_p.exe
%{_bindir}/g1print.exe
%{_bindir}/g2print.exe
%{_bindir}/geogrid.exe
%{_bindir}/height_ukmo.exe
%{_bindir}/int2nc.exe
%{_bindir}/metgrid.exe
%{_bindir}/mod_levs.exe
%{_bindir}/plotfmt.exe
%{_bindir}/plotgrids.exe
%{_bindir}/rd_intermediate.exe
%{_bindir}/ungrib.exe
%dir %{_datadir}/WRFV3
%{_datadir}/WRFV3/geogrid/
%{_datadir}/WRFV3/metgrid/


%changelog
* Mon Oct 3 2016 Orion Poplawski <orion@cora.nwra.com> 3.7.1-1
- Polar WRF variant

* Thu Sep 29 2016 Orion Poplawski <orion@cora.nwra.com> 3.8.1-1
- Update to 3.8.1
- Compile with -ipo for Intel version
- Increase parallel build cpus
- Fixup some BuildRequires
- Use NETCDF_* module variables for paths
- Build with altcc ncl

* Tue May 31 2016 Orion Poplawski <orion@cora.nwra.com> 3.8-1
- Update to 3.8
- Altccrpms style

* Thu Dec 11 2008 Orion Poplawski <orion@cora.nwra.com> 3.0.1.1-2
- Move WRF install to %{_bindir} and %{_datadir}/WRFV3
- Add setupwrf

* Thu Nov 20 2008 Orion Poplawski <orion@cora.nwra.com> 3.0.1.1-1
- Combinded WRF/WPS

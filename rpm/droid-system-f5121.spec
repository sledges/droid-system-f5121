%define strip /bin/true
%define __requires_exclude  ^.*$
%define __find_requires     %{nil}
%global debug_package       %{nil}
%define __provides_exclude_from ^.*$

%define device suzu

Name:          droid-system-f5121
Summary:       Built from source /system for Droid HAL adaptations
Version:       0.1.1
Release:       1
Group:         System
License:       Proprietary
BuildRequires: ubu-trusty
BuildRequires: sudo-for-abuild
BuildRequires: droid-src-syspart-full
Source0:       %{name}-%{version}.tgz

%description
%{summary}

%prep

%setup -T -c -n droid-system-f5121
sudo chown -R abuild:abuild /home/abuild/src/droid/
mv /home/abuild/src/droid/* .
mkdir -p external
pushd external
tar -zxf %SOURCE0
if [ -d droid-system-f5121-* ]; then
  mv droid-system-f5121-* droid-system-f5121
fi
popd

%build
droid-make %{?_smp_mflags} libnfc-nci bluetooth.default_32 systemtarball

# Make a tmp location for built installables
rm -rf tmp
mkdir tmp

%install

# Install

tar --list -vf out/target/product/%{device}/system.tar.bz2 > tmp/system-files.txt
tar -xf out/target/product/%{device}/system.tar.bz2 -C $RPM_BUILD_ROOT/

# Get the uid and gid from the tar output and format lines so that those are ok for %files in rpm
cat tmp/system-files.txt | awk '{ split($2,ids,"/"); print "%attr(-," ids[1] "," ids[2] ") /" $6 }' > tmp/system.files.tmp
# Add %dir macro in front of the directories
cat tmp/system.files.tmp | awk '{ if (/\/$/) print "%dir "$0; else print $0}' > tmp/system.files

# HACK: This is a bit ugly, but gets the job done.
# As tar outputs numbers instead of names and rpm wants names, lets replace the id numbers
# with appropriate names here.
sed -i 's/,0/,root/g' tmp/system.files
sed -i 's/,2000/,shell/g' tmp/system.files

# OK -all the stuff from out/ that we need is now extracted
# Clean it up if we're on the OBS and need tmpfs build space:
%if 0%{?_obs_build_project:1}
rm -rf out
# HACK: for some reason this file has 000 perms, causing a failure
chmod +r $RPM_BUILD_ROOT/system/etc/fs_config_files
%endif

%files -f tmp/system.files
%defattr(-,root,root,-)


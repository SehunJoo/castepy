#!/usr/bin/env perl 

#==================================================================================#
#                                   crud.pl                                        #
#==================================================================================#
#                                                                                  #
# This file is part of the AIRSS structure prediction package.                     #
#                                                                                  #
# AIRSS is free software; you can redistribute it and/or modify it under the terms #
# of the GNU General Public License version 2 as published by the Free Software    #
# Foundation.                                                                      #
#                                                                                  #
# This program is distributed in the hope that it will be useful, but WITHOUT ANY  #
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A  #
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.        #           
#                                                                                  #
# You should have received a copy of the GNU General Public License along with this#
# program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street,#                   
# Fifth Floor, Boston, MA  02110-1301, USA.                                        #
#                                                                                  #
#----------------------------------------------------------------------------------#
# The CASTEP Run Daemon (CRUD)                                                     #
#----------------------------------------------------------------------------------#
# Written by Chris Pickard, Copyright (c) 2005-2020                                #
#----------------------------------------------------------------------------------#
#                                                                                  #
#==================================================================================#


use strict;
use Getopt::Long;
use Time::HiRes qw ( sleep );

sub usage {
  printf STDERR "Usage: crud.pl [-launch] [-exec] [-mpinp xx] [-repose] [-ramble] [-keep] [-nostop] [-cycle] [-pack]  [-num] [-workdir] Run many castep/repose/ramble computations\n";
  printf STDERR "       -exec           Use this executable\n";
  printf STDERR "       -launch         Use this parallel launcher\n";
  printf STDERR "       -mpinp          Number of cores per mpi Castep (0)\n";
  printf STDERR "       -repose         Use repose (0)\n";
  printf STDERR "       -ramble         Use ramble (0)\n";
  printf STDERR "       -keep           Keep all output files (0)\n";
  printf STDERR "       -nostop         Keep the script running (0)\n";
  printf STDERR "       -cycle          Retry failed runs (0)\n";
  printf STDERR "       -pack           Run with packed data (0)\n";
  printf STDERR "       -num            Max number to unpack (1000)\n";
  printf STDERR "       -workdir        Work directory ('.')\n";
  exit();
}

my ($opt_launch,$opt_exec,$opt_mpinp,$opt_repose,$opt_ramble,$opt_keep,$opt_nostop,$opt_cycle,$opt_pack,$opt_num,$opt_workdir,$opt_help) = ("","",0,0,0,0,0,0,0,1000,".",0);

my $commandline = (join " ", @ARGV);

&GetOptions("launch=s"     => \$opt_launch,
	        "exec=s"       => \$opt_exec,
	        "mpinp=n"      => \$opt_mpinp,
	        "repose"       => \$opt_repose,
	        "ramble"       => \$opt_ramble,
	        "keep"         => \$opt_keep,
	        "nostop"       => \$opt_nostop,
	        "cycle"        => \$opt_cycle,
	        "pack"         => \$opt_pack,
	        "num=n"        => \$opt_num,
	        "workdir=s"    => \$opt_workdir,
            "h|help"       => \$opt_help)|| &usage();

if ($opt_help) {
  &usage();
}

sleep(rand(1));

my $main_thread="no";

if ( system("( set -o noclobber; hostname > main.lock ) 2> /dev/null") == 0 ) {$main_thread="yes"}

my @restars="";
my $restar="";
my $pid=`echo $$`; chomp $pid;

if ( $opt_pack > 0 ) { 
	@restars = `ls -U ./hopper/*.res.tar 2>/dev/null`;
	chomp @restars;
	if (scalar @restars == 0) {print "pack mode requested - no res.tar files found\n"; exit};
	if (scalar @restars > 1) {print "pack mode requested - multiple res.tar files found\n"; exit};
	$restar=@restars[0];
}

# Make work directory

system "mkdir -p $opt_workdir";

do {
  
  my @files = `ls -U hopper | head -$opt_num | grep "\.res\$" | grep "-" | shuf`;
  chomp @files;
  
  if ( $main_thread eq "yes" ) { 
	  	
	  if ( $opt_pack > 0 ) {	  
		  
	  	if( scalar @files < $opt_num ) {
		  
			  my $num_extra = $opt_num - scalar @files;
		  		  
			  my @newfiles = `tar -tf $restar | grep "\.res\$" | grep "-" | head -$num_extra`;
			  chomp @newfiles;
		  		  		  
			  system("tar -xf $restar -C hopper @newfiles && tar -f $restar @newfiles --delete");
		  
			  @files = `ls -U hopper | head -$opt_num | grep "\.res\$" | grep "-" | shuf`;
			  chomp @files;
		  
			  if ( scalar @files == 0 ) {system("rm -f main.lock")}
		  
	 	 }
	  } else {system("rm -f main.lock")}
  }
    	
  my $gotfile=1;
  my $file="";
  
  if (scalar @files == 0) { sleep(rand(1)) ; if ($opt_nostop==0 && ! -f "main.lock") {exit}} ### loop for files here
  
  foreach (@files) {$file = $_; if ( ! -f $opt_workdir."/".$file ) {if (system("mv ./hopper/$file $opt_workdir/.")==0 && -f $opt_workdir."/".$file ){$gotfile=0;last}}}  
    
  if ($gotfile == 0) {
	  
  	$file =~ s/^\.\///;
	  
    my @tmp=split('\.res',$file) ; my $seed=$tmp[0] ; @tmp = split('-',$seed) ; my $root=$tmp[0];
		
    system("(cabal res cell < $opt_workdir/$seed.res ; sed -e '/^%BLOCK [Ll][Aa][Tt]*/, /^%ENDBLOCK [Ll][Aa][Tt]*/d' $root.cell | sed -e '/^%BLOCK [Pp][Oo][Ss]*/, /^%ENDBLOCK [Pp][Oo][Ss]*/d') > $opt_workdir/$seed.cell");

     
    my $executable= 'castep'; 

    if ( $opt_exec ne '' ) {$executable=$opt_exec};

    my $launcher='mpirun -np ';

    if ( $opt_launch ne '' ) {$launcher=$opt_launch};
    
    if ( $opt_mpinp > 0 ) { $executable= '"'.$launcher.$opt_mpinp.' '.$executable.'"' }
    
    system("[[ -f $root.param ]] && cp $root.param $opt_workdir/$seed.param");
    system("[[ -f $root.par ]] && cp $root.par $opt_workdir/$seed.par");
    system("cas-airssspin.py $opt_workdir/$seed.cell");                                                 
    
    if( ($opt_repose > 0) or ($opt_ramble > 0) ) {system("[[ -f $root.ddp ]] && cp $root.ddp $opt_workdir/$seed.ddp 2>/dev/null ; [[ -f $root.eddp ]] && cp $root.eddp $opt_workdir/$seed.eddp 2>/dev/null")} 
    
    # Ensure that the spin in the cell and param are consistent

    my $spintot=`grep -v "#SPIN=" $opt_workdir/$seed.cell | grep SPIN= | awk 'BEGIN {FS="SPIN="};{ sum += \$2 } END {printf "%10.3f",sum}'`;

    open  PARAMFILE, "$opt_workdir/$seed.param" or die $!;
    my @paramdata = <PARAMFILE>;
    close PARAMFILE;
      
    open  PARAMFILE, ">$opt_workdir/$seed.param" or die $!;
    foreach (@paramdata) {
      my @vec = split(' ',$_);
      if ( lc $vec[0] ne "spin" ) {
	print PARAMFILE $_;
      }
      ;
    }
    print PARAMFILE "spin : ".$spintot;
    close PARAMFILE;
      
    if ($opt_mpinp > 0 ) {
      if($opt_repose > 0) {
	      system("(repose_relax repose $opt_mpinp $opt_workdir/$seed)")
      } elsif($opt_ramble > 0){
      	system("(repose_relax ramble $opt_mpinp $opt_workdir/$seed)")
      } else {
      	system("eval $executable $opt_workdir/$seed");
      }
    } else {
      if($opt_repose > 0) {
      	system("repose_relax repose 1 $opt_workdir/$seed")
      }elsif($opt_ramble > 0){
         system("repose_relax ramble 1 $opt_workdir/$seed")  
      } else {
      	system("$executable $opt_workdir/$seed");
      }
    }
      
    if (-e $opt_workdir."/".$seed."-out.cell") {
	
      if (-e $opt_workdir."/".$seed.".dome_bin") {
		  system("(echo 'task : dos';echo 'broadening : linear'; echo 'compute_band_gap : true')>$opt_workdir/$seed.odi;optados $opt_workdir/$seed;rm $opt_workdir/$seed.linear.dat;sed 's/legend 0.85, 0.8/legend 0.2, 0.8/g' $opt_workdir/$seed.linear.agr | sed 's/Electronic Density of States/$seed/g' > $opt_workdir/$seed.dos.agr ; (echo '\@target G0.s1'; echo '\@type xy' ; echo 'EfD 0'; echo 'EfD 5' ; echo '&' ;echo ' @    xaxis ticklabel font 4';echo ' @    yaxis ticklabel font 4') >> $opt_workdir/$seed.dos.agr");
      }
	
      # Construct the res file

      system("castep2res $opt_workdir/$seed > $opt_workdir/$seed.res");

      # Record the command line used
    
      system("sed -i 's/REM COMMAND_LINE/REM cmdline: crud.pl $commandline /g' $opt_workdir/$seed.res");
	
      # Add data to DOS plot
	
      if (-e $opt_workdir."/".$seed.".dos.agr") {
		  my $efd='';
		  if (-e $opt_workdir."/".$seed.".odo") {chomp($efd = `grep EfD $opt_workdir/$seed.odo | tail -1 | awk '{print \$7}'`)}
		  
		  system("mv $opt_workdir/$seed.dos.agr $opt_workdir/$seed.dos.tmp.agr ; sed 's/EfD/$efd/g' $opt_workdir/$seed.dos.tmp.agr | sed 's/Generated by OptaDOS//g' > $opt_workdir/$seed.dos.agr ; rm $opt_workdir/$seed.dos.tmp.agr ")
      }
	  
    } else {
      chomp(my $err_count=`grep -c -m 1 electronic_minimisation $opt_workdir/$seed.*.err`);
      if ( (($err_count)&&($opt_cycle)) > 0 ) {
		  system("mv $opt_workdir/$seed.* hopper")
      } else {
		  system("mkdir -p bad_castep ; mv $opt_workdir/$seed.* bad_castep")
      }
    }
	
    if (! $opt_keep) {
      my @delete_files = <$opt_workdir/$seed.*>;
      foreach (@delete_files) {
		  my @tmp = split('\.',$_); my $type=$tmp[-1];
		  if (($type ne "res")&&($type ne "cif")&&($type ne "magres")&&($type ne "castep")&&($type ne "odo")&&($type ne "dos")&&($type ne "den_fmt")) {unlink($_)}	
      }
      unlink($opt_workdir."/".$seed."-out.cell");
    }

    if ( -f $opt_workdir."/".$seed.".res" ) {system("mkdir -p good_castep")}
		
  	if ( $opt_pack > 0 ) {
		if ( -f $opt_workdir."/".$seed.".res" ) {
			
			my $files=`cd $opt_workdir; echo $seed.*`; chomp $files;
			
			system("tar -rf good_castep/$root-$pid.res.tar -C $opt_workdir $files --remove-files");
			
		}
	} else {
		if ( -f $opt_workdir."/".$seed.".res" ) {system("mv -f $opt_workdir/$seed.* good_castep ; [[ -f $opt_workdir/$seed-out.cell ]] && mv -f $opt_workdir/$seed-out.cell good_castep")}
	}
 
    }
    
} until( -e "STOP_CRUD");  
  

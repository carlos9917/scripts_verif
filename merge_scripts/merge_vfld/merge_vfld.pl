#!/usr/bin/perl -w

# Merge several vobs files where the expected name is vobsYYYYMMDDHH*
# The output files is written as vobsYYYYMMDDHH.merged
# In case of dubplicates the new value is always used.
# 
# Ulf Andrae, SMHI, 2017
#

# Carlos small addition: use Basename to be able
# to extract filename from path. Use whole filename paths instead of single name
# Should also work with filename only!
#
# Carlos extra small change: modify to be able to process vfld files instead
# The corresponding vfld files are first linked to dummy 
# arg1: first file (old)
# arg2: second file (new)
# arg3: model name for file1
# arg4: model name for file2

use File::Basename;
my $inpath = "";

my $misval = -99.0000E+00 ;
my $eps    = 1.e-5;

my %synop = ();
my %temp = ();


my $infile = "";
my $date = "" ;

my @TVARS = ();
my @TACC = ();

my $nsynop = 0;
my $ntemp = 0;
my $version = 0;

my $numArgs = $#ARGV + 1;

my @fnames = ($ARGV[0],$ARGV[1]);
my @mnames = ($ARGV[2],$ARGV[3]);

#foreach $inpath (@ARGV) {
foreach $inpath (0..1) {
 $infile_tail = basename($fnames[$inpath]);
 $tmp = $infile_tail ;
 $tmp =~ s/vfld$mnames[$inpath]((\d){12})(.*)/$1/;
 $date=$tmp  if ( $date eq "" )  ;

 die "Mismatch in dates ($date,$tmp) in input files\n" if ( $tmp ne $date ) ;
 
 &merge_data($fnames[$inpath]);

}

$outfile="vfld${date}.merged";

&print_data($outfile);

########################################################################################

sub merge_data (){

 my $infile = shift ;
open FILE, "< $infile" or die "Could not open $infile \n";

 #
 # Handle header 
 #

 $head = <FILE> ; chomp $head ;
 $head =~ s/( ){1,}/ /g;
 ($nsynop,$ntemp,$version) = split(' ',$head);
 #print "$nsynop $ntemp $version\n";
 $nparam = <FILE> ; chomp $nparam ;
# print "$nparam \n";
 my @SVARS = ();
 my @SACC = ();
 for ( $i = 1 ; $i <= $nparam ; $i++ ) {
  $tmp = <FILE> ; chomp $tmp ;
  $tmp =~ s/( ){1,}/ /g;
  
  ($var,$acc) = split(' ',$tmp);
  push(@SVARS,$var);
  push(@SACC,$acc);
  #print "$var $acc \n";
 }
 if ( exists($synop{SVARS}) ) {
  $i = 0;
  foreach $var (@SVARS) {
   unless ( grep /$var/, @{ $synop{SVARS} } ) {
    push (@{ $synop{SVARS} },$var)  ;
    push (@{ $synop{SACC}  },$SACC[$i])  ; 
   }
   $i++ ;
  }
 } else {
   $synop{SVARS}= [ @SVARS ] ;
   $synop{SACC} = [ @SACC  ] ;
 }

 #
 # Handle SYNOP data 
 #

 for ( $i = 1 ; $i <= $nsynop ; $i++ ) {
  $tmp = <FILE> ; chomp $tmp;
  #print "IN:$tmp\n";
  $tmp =~ s/( ){1,}/ /g;
  @tmp = split(' ',$tmp);
  $stnid = shift @tmp;
  $nstnid = $stnid * 1 ;
  $lat = shift @tmp;
  $lon = shift @tmp;
  $hgt = shift @tmp;
  $hgt = $misval if (  $hgt == -256 ) ;

#  print "$nstnid: $stnid $lat $lon $hgt\n";
  if ( exists($synop{$nstnid}) ) {

   #
   # Merge station information
   #

   #print "Merge station $stnid/$synop{$nstnid}{STNID}\n";

   #print " Mismatch in LAT: $synop{$nstnid}{LAT},$lat\n" unless ( $synop{$nstnid}{LAT} eq $lat ) ;
   #print " Mismatch in LON: $synop{$nstnid}{LON},$lon\n" unless ( $synop{$nstnid}{LON} eq $lon ) ;
   #print " Mismatch in HGT: $synop{$nstnid}{HGT},$hgt\n" unless ( $synop{$nstnid}{HGT} eq $hgt ) ;
   #die ;
   foreach $var (@SVARS) {
    $tmp = shift @tmp ;
    if ( exists($synop{$nstnid}{$var}) && abs($synop{$nstnid}{$var}-$misval) > $eps ) {

     if ( abs($synop{$nstnid}{$var}-$tmp)>$eps && abs($tmp-$misval) > $eps ) {
      print "Double $var, use new\n";
      print "Old: $synop{$nstnid}{$var} \n" ;
      print "New: $tmp \n";
      $synop{$nstnid}{$var} = $tmp ;
     }

    } else {
     $synop{$nstnid}{$var} = $tmp ;
     #print"Added $var:$synop{$nstnid}{$var}\n";
    }
   }
  
  } else {

   #
   # New station
   #

   $synop{$nstnid}{STNID} = $stnid ;
   $synop{$nstnid}{LAT} = $lat ;
   $synop{$nstnid}{LON} = $lon ;
   $synop{$nstnid}{HGT} = $hgt ;
   #print "@tmp\n"   ;
   foreach $var (@SVARS) {
    $synop{$nstnid}{$var} = shift @tmp ;
   # print"Added $var:$synop{$nstnid}{$var}\n";
   }
   if ( 0 ) {
   @tmp = ();
   push (@tmp,$synop{$nstnid}{STNID});
   push (@tmp,$synop{$nstnid}{LAT});
   push (@tmp,$synop{$nstnid}{LON});
   push (@tmp,$synop{$nstnid}{HGT});
   foreach $var (@SVARS) {
    push (@tmp,$synop{$nstnid}{$var});
   }
    print "@tmp\n";
   }
  }
 }

 if ( $ntemp == 0 ) {
  close FILE ;
  return ;
 }

 #
 # Handle TEMP data 
 #
 $nlev = <FILE> ; chomp $nlev;
 $temp{NLEV} = $nlev ;
 $nparam = <FILE> ; chomp $nparam ;
 $temp{NPARAM} = $nparam ;

 for ( $i = 1 ; $i <= $nparam ; $i++ ) {
  $tmp = <FILE> ; chomp $tmp ;
  $tmp =~ s/( ){1,}/ /g;
  
  ($var,$acc) = split(' ',$tmp);
  push(@TVARS,$var);
  push(@TACC,$acc);
  #print "$var $acc \n";
 }

 for ( $i = 1 ; $i <= $ntemp ; $i++ ) {
  $tmp = <FILE> ; chomp $tmp;
  print "IN:$tmp\n";
  $tmp =~ s/( ){1,}/ /g;
  ($stnid,$lat,$lon,$hgt) = split(' ',$tmp);
  print "read: $stnid $lat $lon $hgt \n";
  $nstnid = $stnid * 1 ;
  print "$nstnid: $stnid $lat $lon $hgt\n";
  if ( exists($temp{$nstnid}) ) {

   die "Not coded yet\n";
  
  } else {

   #
   # New station
   #

   $temp{$nstnid}{STNID} = $stnid ;
   $temp{$nstnid}{LAT} = $lat ;
   $temp{$nstnid}{LON} = $lon ;
   $temp{$nstnid}{HGT} = $hgt ;
   for ( $j = 1 ; $j <= $nlev ; $j++ ) {
     $tmp = <FILE> ; chomp $tmp;
     $temp{$nstnid}{$j} = $tmp ;
   }
  }
 }

close FILE;

}

########################################################################################

sub print_data (){


 my $file = shift;

 my @SVARS = @{ $synop{SVARS} };
 my @SACC  = @{ $synop{SACC} };

 delete($synop{SVARS});
 delete($synop{SACC} );

 my $nsynop = keys %synop ;
 my $ntemp  =  keys %temp ;
 $ntemp = $ntemp - 2 if ( $ntemp > 0 ) ;

 my $nsvars = scalar(@SVARS) ;
 
 open FILE, "> $file";
 print "Opened file $file \n";

 printf FILE ("%7s%6s%6s\n",$nsynop, $ntemp, $version);
 printf FILE ("%12s\n", $nsvars);
 $i=0 ; 
 foreach $var (@SVARS) {
  printf FILE (" %-6s%12s\n",$var,$SACC[$i]) ;
  $i++;
 } 
 foreach $nstnid ( sort { $a <=> $b } keys %synop ) {

   @tmp = ();
   print "Print $synop{$nstnid}{STNID}\n";
   push (@tmp,$synop{$nstnid}{STNID});
   push (@tmp,$synop{$nstnid}{LAT});
   push (@tmp,$synop{$nstnid}{LON});
   push (@tmp,$synop{$nstnid}{HGT});
   $size = @tmp; 
   #print "size before loop $size \n";
   foreach $var (@SVARS) {
    if ( exists($synop{$nstnid}{$var}) ) {
     push (@tmp,$synop{$nstnid}{$var});
   $size = @tmp; 
   #print "size in loop $size \n";
    } else {
     push (@tmp,-99.0);
   $size = @tmp; 
    }
   }
   $size = @tmp; 
   # print "size $size \n";
   print FILE "@tmp\n";
   #die ;
 }
 if ( $ntemp > 0 ) {
  $nlev = $temp{NLEV};
  delete ($temp{NLEV});
  print FILE "$nlev\n";
  print FILE "$temp{NPARAM}\n";
  delete ($temp{NPARAM});
  $i=0 ; 
  foreach $var (@TVARS) {
   printf FILE (" %-6s%8s\n",$var,$TACC[$i]) ;
  } 
  foreach $nstnid ( sort { $a <=> $b } keys %temp ) {
   @tmp = ();
   push (@tmp,$temp{$nstnid}{STNID});
   push (@tmp,$temp{$nstnid}{LAT});
   push (@tmp,$temp{$nstnid}{LON});
   push (@tmp,$temp{$nstnid}{HGT});
   #print FILE " @tmp\n";
   printf FILE ("%6s%9s%9s%8s\n",@tmp);
   for ( $j = 1 ; $j <= $nlev ; $j++ ) {
    print FILE "$temp{$nstnid}{$j}\n";
   }
  }
 }


}

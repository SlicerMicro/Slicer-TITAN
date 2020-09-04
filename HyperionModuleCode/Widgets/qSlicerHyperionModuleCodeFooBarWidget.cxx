/*==============================================================================

  Program: 3D Slicer

  Copyright (c) Kitware Inc.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
  and was partially funded by NIH grant 3P41RR013218-12S1

==============================================================================*/

// FooBar Widgets includes
#include "qSlicerHyperionModuleCodeFooBarWidget.h"
#include "ui_qSlicerHyperionModuleCodeFooBarWidget.h"

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_HyperionModuleCode
class qSlicerHyperionModuleCodeFooBarWidgetPrivate
  : public Ui_qSlicerHyperionModuleCodeFooBarWidget
{
  Q_DECLARE_PUBLIC(qSlicerHyperionModuleCodeFooBarWidget);
protected:
  qSlicerHyperionModuleCodeFooBarWidget* const q_ptr;

public:
  qSlicerHyperionModuleCodeFooBarWidgetPrivate(
    qSlicerHyperionModuleCodeFooBarWidget& object);
  virtual void setupUi(qSlicerHyperionModuleCodeFooBarWidget*);
};

// --------------------------------------------------------------------------
qSlicerHyperionModuleCodeFooBarWidgetPrivate
::qSlicerHyperionModuleCodeFooBarWidgetPrivate(
  qSlicerHyperionModuleCodeFooBarWidget& object)
  : q_ptr(&object)
{
}

// --------------------------------------------------------------------------
void qSlicerHyperionModuleCodeFooBarWidgetPrivate
::setupUi(qSlicerHyperionModuleCodeFooBarWidget* widget)
{
  this->Ui_qSlicerHyperionModuleCodeFooBarWidget::setupUi(widget);
}

//-----------------------------------------------------------------------------
// qSlicerHyperionModuleCodeFooBarWidget methods

//-----------------------------------------------------------------------------
qSlicerHyperionModuleCodeFooBarWidget
::qSlicerHyperionModuleCodeFooBarWidget(QWidget* parentWidget)
  : Superclass( parentWidget )
  , d_ptr( new qSlicerHyperionModuleCodeFooBarWidgetPrivate(*this) )
{
  Q_D(qSlicerHyperionModuleCodeFooBarWidget);
  d->setupUi(this);
}

//-----------------------------------------------------------------------------
qSlicerHyperionModuleCodeFooBarWidget
::~qSlicerHyperionModuleCodeFooBarWidget()
{
}
